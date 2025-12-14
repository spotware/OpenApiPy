#!/usr/bin/env python3
"""
Real-time Market Data Handler for cTrader Open API
Implements on_tick and on_bar callbacks for live market data streaming

Features:
- Real-time tick data (bid/ask prices)
- Live trendbar/candlestick data
- Multiple symbol support
- Customizable callback functions
- Data filtering and processing
- Comprehensive error handling

Author: Claude Code Assistant
"""

import datetime
import time
import json
import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from twisted.internet import reactor, task

from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TickData:
    """Structure for tick data"""
    symbol_id: int
    symbol_name: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime.datetime
    raw_timestamp: int

    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid + self.ask) / 2.0


@dataclass
class BarData:
    """Structure for bar/candlestick data"""
    symbol_id: int
    symbol_name: str
    period: str
    open_time: datetime.datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    timestamp: datetime.datetime

    @property
    def body_size(self) -> float:
        """Calculate bar body size"""
        return abs(self.close_price - self.open_price)

    @property
    def upper_shadow(self) -> float:
        """Calculate upper shadow/wick"""
        return self.high_price - max(self.open_price, self.close_price)

    @property
    def lower_shadow(self) -> float:
        """Calculate lower shadow/wick"""
        return min(self.open_price, self.close_price) - self.low_price

    @property
    def is_bullish(self) -> bool:
        """Check if bar is bullish (close > open)"""
        return self.close_price > self.open_price


class MarketDataHandler:
    def __init__(self, credentials_file="credentials.json"):
        """
        Initialize the Market Data Handler

        Args:
            credentials_file (str): Path to credentials JSON file
        """
        self.credentials_file = credentials_file
        self.credentials = None
        self.client = None
        self.account_id = None
        self.is_authenticated = False
        self.is_connected = False

        # Symbol management
        self.symbols = {}  # symbol_name -> symbol_id
        self.symbol_ids = {}  # symbol_id -> symbol_name
        self.subscribed_spots = set()  # Set of subscribed symbol IDs for spots
        self.subscribed_bars = {}  # symbol_id -> period mapping

        # Callback functions
        self.on_tick_callback: Optional[Callable[[TickData], None]] = None
        self.on_bar_callback: Optional[Callable[[BarData], None]] = None
        self.on_connection_callback: Optional[Callable[[], None]] = None
        self.on_disconnection_callback: Optional[Callable[[str], None]] = None

        # Statistics
        self.tick_count = 0
        self.bar_count = 0
        self.start_time = None

        # Load credentials and setup
        self.load_credentials()
        self.setup_client()

    def load_credentials(self):
        """Load cTrader API credentials"""
        try:
            with open(self.credentials_file, 'r') as f:
                self.credentials = json.load(f)
            self.account_id = self.credentials["AccountId"]
            logger.info(f"📋 Loaded credentials for account: {self.account_id}")
        except Exception as e:
            logger.error(f"❌ Failed to load credentials: {e}")
            raise

    def setup_client(self):
        """Setup cTrader API client"""
        try:
            host_type = self.credentials["HostType"].lower()
            if host_type == "live":
                host = EndPoints.PROTOBUF_LIVE_HOST
                logger.warning("⚠️  Using LIVE account")
            else:
                host = EndPoints.PROTOBUF_DEMO_HOST
                logger.info("🔧 Using demo account")

            self.client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

            # Set callbacks
            self.client.setConnectedCallback(self.on_connected)
            self.client.setDisconnectedCallback(self.on_disconnected)
            self.client.setMessageReceivedCallback(self.on_message_received)

        except Exception as e:
            logger.error(f"❌ Failed to setup client: {e}")
            raise

    def on_connected(self, client):
        """Callback when connected to server"""
        logger.info("✅ Connected to cTrader server")
        self.is_connected = True
        self.start_time = datetime.datetime.now()
        self.authenticate_application()

        if self.on_connection_callback:
            self.on_connection_callback()

    def on_disconnected(self, client, reason):
        """Callback when disconnected from server"""
        logger.warning(f"❌ Disconnected: {reason}")
        self.is_connected = False
        self.is_authenticated = False
        self.subscribed_spots.clear()
        self.subscribed_bars.clear()

        if self.on_disconnection_callback:
            self.on_disconnection_callback(str(reason))

    def on_message_received(self, client, message):
        """Handle all incoming messages"""
        try:
            # Handle spot events (tick data)
            if message.payloadType == ProtoOASpotEvent().payloadType:
                self.handle_spot_event(message)

            # Handle other message types
            elif message.payloadType not in [ProtoHeartbeatEvent().payloadType]:
                logger.debug(f"📨 Received message type: {message.payloadType}")

        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")

    def handle_spot_event(self, message):
        """Handle incoming spot events (tick data)"""
        try:
            spot_data = Protobuf.extract(message)

            # Extract tick information
            symbol_id = spot_data.symbolId
            symbol_name = self.symbol_ids.get(symbol_id, f"Symbol_{symbol_id}")

            # Convert prices from raw format
            bid = spot_data.bid / 100000.0 if spot_data.bid else 0.0
            ask = spot_data.ask / 100000.0 if spot_data.ask else 0.0
            spread = ask - bid if (ask and bid) else 0.0

            # Create timestamp
            raw_timestamp = spot_data.timestamp if hasattr(spot_data, 'timestamp') and spot_data.timestamp else int(time.time() * 1000)
            timestamp = datetime.datetime.fromtimestamp(raw_timestamp / 1000.0)

            # Create tick data object
            tick = TickData(
                symbol_id=symbol_id,
                symbol_name=symbol_name,
                bid=bid,
                ask=ask,
                spread=spread,
                timestamp=timestamp,
                raw_timestamp=raw_timestamp
            )

            # Update statistics
            self.tick_count += 1

            # Log tick (reduce frequency to avoid spam)
            if self.tick_count % 100 == 0:
                logger.info(f"📊 Tick #{self.tick_count}: {symbol_name} Bid: {bid:.5f}, Ask: {ask:.5f}, Spread: {spread:.5f}")

            # Call user callback
            if self.on_tick_callback:
                self.on_tick_callback(tick)

            # Handle trendbar data within spot event
            if hasattr(spot_data, 'trendbar') and spot_data.trendbar:
                for trendbar in spot_data.trendbar:
                    self.handle_trendbar(symbol_id, symbol_name, trendbar)

        except Exception as e:
            logger.error(f"❌ Error handling spot event: {e}")

    def handle_trendbar(self, symbol_id: int, symbol_name: str, trendbar):
        """Handle trendbar data"""
        try:
            # Extract trendbar information
            open_time = datetime.datetime.fromtimestamp(trendbar.utcTimestampInMinutes * 60, datetime.timezone.utc)
            open_price = (trendbar.low + trendbar.deltaOpen) / 100000.0
            high_price = (trendbar.low + trendbar.deltaHigh) / 100000.0
            low_price = trendbar.low / 100000.0
            close_price = (trendbar.low + trendbar.deltaClose) / 100000.0
            volume = trendbar.volume

            # Determine period (you might need to track this separately)
            period = "Unknown"  # This would need to be tracked based on subscription

            # Create bar data object
            bar = BarData(
                symbol_id=symbol_id,
                symbol_name=symbol_name,
                period=period,
                open_time=open_time,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                timestamp=datetime.datetime.now()
            )

            # Update statistics
            self.bar_count += 1

            logger.info(f"📈 Bar #{self.bar_count}: {symbol_name} {period} O:{open_price:.5f} H:{high_price:.5f} L:{low_price:.5f} C:{close_price:.5f} V:{volume}")

            # Call user callback
            if self.on_bar_callback:
                self.on_bar_callback(bar)

        except Exception as e:
            logger.error(f"❌ Error handling trendbar: {e}")

    def authenticate_application(self):
        """Authenticate application"""
        logger.info("🔐 Authenticating application...")

        request = ProtoOAApplicationAuthReq()
        request.clientId = self.credentials["ClientId"]
        request.clientSecret = self.credentials["Secret"]

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_application_auth_success, self.on_error)

    def on_application_auth_success(self, result):
        """Application authentication successful"""
        logger.info("✅ Application authenticated")
        self.authenticate_account()

    def authenticate_account(self):
        """Authenticate trading account"""
        logger.info("🔐 Authenticating account...")

        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = self.account_id
        request.accessToken = self.credentials["AccessToken"]

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_account_auth_success, self.on_error)

    def on_account_auth_success(self, result):
        """Account authentication successful"""
        logger.info("✅ Account authenticated")
        self.is_authenticated = True
        self.get_symbols_list()

    def get_symbols_list(self):
        """Get available symbols"""
        logger.info("📋 Getting symbols list...")

        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.account_id
        request.includeArchivedSymbols = False

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_symbols_received, self.on_error)

    def on_symbols_received(self, result):
        """Process symbols list"""
        symbols_data = Protobuf.extract(result)

        for symbol in symbols_data.symbol:
            self.symbols[symbol.symbolName] = symbol.symbolId
            self.symbol_ids[symbol.symbolId] = symbol.symbolName

        logger.info(f"✅ Loaded {len(self.symbols)} symbols")
        logger.info("🚀 Market Data Handler is ready!")

    def subscribe_to_ticks(self, symbol_name: str, subscribe_to_timestamp: bool = True):
        """
        Subscribe to tick data for a symbol

        Args:
            symbol_name (str): Symbol name (e.g., "EURUSD")
            subscribe_to_timestamp (bool): Include timestamp in tick data
        """
        if not self.is_authenticated:
            logger.error("❌ Not authenticated - cannot subscribe to ticks")
            return False

        if symbol_name not in self.symbols:
            logger.error(f"❌ Symbol '{symbol_name}' not found")
            return False

        symbol_id = self.symbols[symbol_name]

        if symbol_id in self.subscribed_spots:
            logger.warning(f"⚠️  Already subscribed to {symbol_name} ticks")
            return True

        logger.info(f"📊 Subscribing to {symbol_name} tick data...")

        try:
            request = ProtoOASubscribeSpotsReq()
            request.ctidTraderAccountId = self.account_id
            request.symbolId.append(symbol_id)
            request.subscribeToSpotTimestamp = subscribe_to_timestamp

            deferred = self.client.send(request)
            deferred.addCallbacks(
                lambda result, sym_id=symbol_id, sym_name=symbol_name: self.on_tick_subscription_success(result, sym_id, sym_name),
                self.on_error
            )

            self.subscribed_spots.add(symbol_id)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {symbol_name} ticks: {e}")
            return False

    def subscribe_to_bars(self, symbol_name: str, period: str):
        """
        Subscribe to live bar data for a symbol

        Args:
            symbol_name (str): Symbol name (e.g., "EURUSD")
            period (str): Period name (e.g., "M1", "H1", "D1")
        """
        if not self.is_authenticated:
            logger.error("❌ Not authenticated - cannot subscribe to bars")
            return False

        if symbol_name not in self.symbols:
            logger.error(f"❌ Symbol '{symbol_name}' not found")
            return False

        symbol_id = self.symbols[symbol_name]

        # Convert period string to enum value
        period_enum = getattr(ProtoOATrendbarPeriod, period, None)
        if period_enum is None:
            logger.error(f"❌ Invalid period '{period}'")
            return False

        logger.info(f"📈 Subscribing to {symbol_name} {period} bar data...")

        try:
            request = ProtoOASubscribeLiveTrendbarReq()
            request.ctidTraderAccountId = self.account_id
            request.period = period_enum
            request.symbolId = symbol_id

            deferred = self.client.send(request)
            deferred.addCallbacks(
                lambda result, sym_id=symbol_id, sym_name=symbol_name, per=period: self.on_bar_subscription_success(result, sym_id, sym_name, per),
                self.on_error
            )

            self.subscribed_bars[symbol_id] = period
            return True

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {symbol_name} {period} bars: {e}")
            return False

    def on_tick_subscription_success(self, result, symbol_id: int, symbol_name: str):
        """Tick subscription successful"""
        logger.info(f"✅ Successfully subscribed to {symbol_name} tick data")

    def on_bar_subscription_success(self, result, symbol_id: int, symbol_name: str, period: str):
        """Bar subscription successful"""
        logger.info(f"✅ Successfully subscribed to {symbol_name} {period} bar data")

    def unsubscribe_from_ticks(self, symbol_name: str):
        """Unsubscribe from tick data"""
        if symbol_name not in self.symbols:
            logger.error(f"❌ Symbol '{symbol_name}' not found")
            return False

        symbol_id = self.symbols[symbol_name]

        if symbol_id not in self.subscribed_spots:
            logger.warning(f"⚠️  Not subscribed to {symbol_name} ticks")
            return True

        logger.info(f"📊 Unsubscribing from {symbol_name} tick data...")

        try:
            request = ProtoOAUnsubscribeSpotsReq()
            request.ctidTraderAccountId = self.account_id
            request.symbolId.append(symbol_id)

            deferred = self.client.send(request)
            deferred.addCallbacks(self.on_success, self.on_error)

            self.subscribed_spots.discard(symbol_id)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe from {symbol_name} ticks: {e}")
            return False

    def set_on_tick_callback(self, callback: Callable[[TickData], None]):
        """Set callback function for tick data"""
        self.on_tick_callback = callback
        logger.info("✅ Tick callback set")

    def set_on_bar_callback(self, callback: Callable[[BarData], None]):
        """Set callback function for bar data"""
        self.on_bar_callback = callback
        logger.info("✅ Bar callback set")

    def set_on_connection_callback(self, callback: Callable[[], None]):
        """Set callback for connection events"""
        self.on_connection_callback = callback

    def set_on_disconnection_callback(self, callback: Callable[[str], None]):
        """Set callback for disconnection events"""
        self.on_disconnection_callback = callback

    def get_statistics(self):
        """Get statistics"""
        uptime = datetime.datetime.now() - self.start_time if self.start_time else datetime.timedelta(0)

        return {
            'is_connected': self.is_connected,
            'is_authenticated': self.is_authenticated,
            'uptime': str(uptime),
            'tick_count': self.tick_count,
            'bar_count': self.bar_count,
            'subscribed_symbols_ticks': len(self.subscribed_spots),
            'subscribed_symbols_bars': len(self.subscribed_bars),
            'available_symbols': len(self.symbols)
        }

    def on_success(self, result):
        """Generic success callback"""
        logger.debug("✅ Operation successful")

    def on_error(self, failure):
        """Generic error callback"""
        logger.error(f"❌ API Error: {failure}")

    def start(self):
        """Start the market data handler"""
        logger.info("🚀 Starting Market Data Handler...")
        self.client.startService()

    def stop(self):
        """Stop the market data handler"""
        logger.info("⏹️  Stopping Market Data Handler...")
        self.client.stopService()


# Example usage and callback implementations
def example_on_tick(tick: TickData):
    """Example tick callback function"""
    print(f"🔔 TICK: {tick.symbol_name} | Bid: {tick.bid:.5f} | Ask: {tick.ask:.5f} | Spread: {tick.spread:.5f} | Time: {tick.timestamp.strftime('%H:%M:%S.%f')[:-3]}")

def example_on_bar(bar: BarData):
    """Example bar callback function"""
    direction = "🟢 BULL" if bar.is_bullish else "🔴 BEAR"
    print(f"📊 BAR: {bar.symbol_name} {bar.period} | {direction} | O: {bar.open_price:.5f} | H: {bar.high_price:.5f} | L: {bar.low_price:.5f} | C: {bar.close_price:.5f} | V: {bar.volume}")

def example_on_connection():
    """Example connection callback"""
    print("🟢 Connected to market data feed!")

def example_on_disconnection(reason: str):
    """Example disconnection callback"""
    print(f"🔴 Disconnected from market data feed: {reason}")


def main():
    """Example usage"""
    logger.info("🚀 Starting Market Data Handler Example")

    try:
        # Create handler
        handler = MarketDataHandler()

        # Set callbacks
        handler.set_on_tick_callback(example_on_tick)
        handler.set_on_bar_callback(example_on_bar)
        handler.set_on_connection_callback(example_on_connection)
        handler.set_on_disconnection_callback(example_on_disconnection)

        # Start the handler
        handler.start()

        # Wait for authentication, then subscribe
        def subscribe_after_auth():
            if handler.is_authenticated:
                logger.info("🔔 Setting up subscriptions...")

                # Subscribe to tick data
                handler.subscribe_to_ticks("EURUSD", True)
                handler.subscribe_to_ticks("GBPUSD", True)

                # Subscribe to bar data
                handler.subscribe_to_bars("EURUSD", "M1")  # 1-minute bars

            else:
                # Check again in 1 second
                reactor.callLater(1, subscribe_after_auth)

        # Start subscription attempt after 3 seconds
        reactor.callLater(3, subscribe_after_auth)

        # Log statistics every 30 seconds
        def log_stats():
            stats = handler.get_statistics()
            logger.info("📊 Statistics:")
            logger.info(f"   Connected: {stats['is_connected']}")
            logger.info(f"   Uptime: {stats['uptime']}")
            logger.info(f"   Ticks received: {stats['tick_count']}")
            logger.info(f"   Bars received: {stats['bar_count']}")
            logger.info(f"   Subscribed symbols (ticks): {stats['subscribed_symbols_ticks']}")
            logger.info(f"   Subscribed symbols (bars): {stats['subscribed_symbols_bars']}")
            reactor.callLater(30, log_stats)

        reactor.callLater(10, log_stats)

        # Run reactor
        logger.info("🎯 Market data handler started! Press Ctrl+C to stop.")
        reactor.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        handler.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()