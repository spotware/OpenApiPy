#!/usr/bin/env python3
"""
Scheduled cTrader Trading Bot
Opens a buy position every day at 9:00 AM

IMPORTANT WARNINGS:
1. This trades with REAL MONEY on live markets
2. Test thoroughly with demo account first
3. Set appropriate position sizes to limit risk
4. Monitor trades regularly
5. Have a risk management strategy

Author: Claude Code Assistant
"""

import datetime
import time
import schedule
import json
import calendar
import logging
from threading import Thread
from twisted.internet import reactor, task
from twisted.application import service

from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScheduledTrader:
    def __init__(self, credentials_file="credentials.json"):
        """
        Initialize the scheduled trader

        Args:
            credentials_file (str): Path to credentials JSON file
        """
        self.credentials_file = credentials_file
        self.credentials = None
        self.client = None
        self.account_id = None
        self.symbol_id = None
        self.symbol_name = "EURUSD"  # Default symbol to trade
        self.volume = 1000  # Default volume (0.01 lots = 1000 units)
        self.is_authenticated = False
        self.is_connected = False

        # Load credentials
        self.load_credentials()

        # Initialize client
        self.setup_client()

    def load_credentials(self):
        """Load cTrader API credentials from JSON file"""
        try:
            with open(self.credentials_file, 'r') as f:
                self.credentials = json.load(f)
            self.account_id = self.credentials["AccountId"]
            logger.info(f"Loaded credentials for account: {self.account_id}")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise

    def setup_client(self):
        """Initialize cTrader API client"""
        try:
            # Select host based on credentials
            host_type = self.credentials["HostType"].lower()
            if host_type == "live":
                host = EndPoints.PROTOBUF_LIVE_HOST
                logger.warning("⚠️  USING LIVE ACCOUNT - REAL MONEY TRADING!")
            else:
                host = EndPoints.PROTOBUF_DEMO_HOST
                logger.info("Using demo account")

            # Create client
            self.client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

            # Set callbacks
            self.client.setConnectedCallback(self.on_connected)
            self.client.setDisconnectedCallback(self.on_disconnected)
            self.client.setMessageReceivedCallback(self.on_message_received)

        except Exception as e:
            logger.error(f"Failed to setup client: {e}")
            raise

    def on_connected(self, client):
        """Callback when client connects to server"""
        logger.info("✅ Connected to cTrader server")
        self.is_connected = True

        # Start authentication process
        self.authenticate_application()

    def on_disconnected(self, client, reason):
        """Callback when client disconnects"""
        logger.warning(f"❌ Disconnected from server: {reason}")
        self.is_connected = False
        self.is_authenticated = False

    def on_message_received(self, client, message):
        """Callback for all received messages"""
        # Filter out common messages to reduce noise
        if message.payloadType not in [ProtoHeartbeatEvent().payloadType]:
            logger.debug(f"Received message: {message.payloadType}")

    def authenticate_application(self):
        """Step 1: Authenticate the application"""
        logger.info("🔐 Authenticating application...")

        request = ProtoOAApplicationAuthReq()
        request.clientId = self.credentials["ClientId"]
        request.clientSecret = self.credentials["Secret"]

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_application_auth_success, self.on_error)

    def on_application_auth_success(self, result):
        """Application authentication successful"""
        logger.info("✅ Application authenticated")

        # Step 2: Authenticate trading account
        self.authenticate_account()

    def authenticate_account(self):
        """Step 2: Authenticate the trading account"""
        logger.info("🔐 Authenticating trading account...")

        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = self.account_id
        request.accessToken = self.credentials["AccessToken"]

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_account_auth_success, self.on_error)

    def on_account_auth_success(self, result):
        """Account authentication successful"""
        logger.info("✅ Trading account authenticated")
        self.is_authenticated = True

        # Step 3: Get symbols list and find our trading symbol
        self.get_symbols_list()

    def get_symbols_list(self):
        """Step 3: Get list of available symbols"""
        logger.info(f"📋 Getting symbols list to find {self.symbol_name}...")

        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.account_id
        request.includeArchivedSymbols = False

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_symbols_received, self.on_error)

    def on_symbols_received(self, result):
        """Symbols list received"""
        symbols = Protobuf.extract(result)

        # Find our target symbol
        matching_symbols = [s for s in symbols.symbol if s.symbolName == self.symbol_name]

        if not matching_symbols:
            logger.error(f"❌ Symbol '{self.symbol_name}' not found in account")
            return
        elif len(matching_symbols) > 1:
            logger.warning(f"⚠️  Multiple matches for '{self.symbol_name}', using first one")

        self.symbol_id = matching_symbols[0].symbolId
        logger.info(f"✅ Found symbol {self.symbol_name} with ID: {self.symbol_id}")

        # Setup complete
        logger.info("🚀 Trading bot is ready for scheduled trades!")

    def create_market_buy_order(self):
        """Create a market buy order"""
        if not self.is_authenticated or not self.symbol_id:
            logger.error("❌ Cannot create order - not authenticated or symbol not found")
            return

        logger.info(f"🛒 Creating BUY market order for {self.symbol_name}")
        logger.info(f"   Volume: {self.volume} units ({self.volume/100000:.2f} lots)")

        try:
            request = ProtoOANewOrderReq()
            request.ctidTraderAccountId = self.account_id
            request.symbolId = self.symbol_id
            request.orderType = ProtoOAOrderType.MARKET  # Market order
            request.tradeSide = ProtoOATradeSide.BUY     # Buy side
            request.volume = self.volume  # Volume in smallest units

            # Optional: Add stop loss and take profit (in pips or absolute price)
            # request.stopLoss = 1.1000  # Stop loss level
            # request.takeProfit = 1.1200  # Take profit level

            # Optional: Add comment
            request.comment = f"Scheduled buy {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

            deferred = self.client.send(request)
            deferred.addCallbacks(self.on_order_success, self.on_error)

        except Exception as e:
            logger.error(f"❌ Failed to create order: {e}")

    def on_order_success(self, result):
        """Order successfully created"""
        logger.info("✅ Market buy order created successfully!")
        # You might want to log order details or send notifications here

    def on_error(self, failure):
        """Error callback for failed requests"""
        logger.error(f"❌ API Error: {failure}")

    def start_client(self):
        """Start the cTrader client"""
        if self.client:
            logger.info("🔄 Starting cTrader client service...")
            self.client.startService()

    def stop_client(self):
        """Stop the cTrader client"""
        if self.client:
            logger.info("⏹️  Stopping cTrader client service...")
            self.client.stopService()

    def schedule_daily_trade(self, trade_time="09:00"):
        """
        Schedule daily trading at specified time

        Args:
            trade_time (str): Time to execute trade in HH:MM format
        """
        logger.info(f"📅 Scheduling daily BUY orders at {trade_time}")

        # Schedule the trade
        schedule.every().day.at(trade_time).do(self.execute_scheduled_trade)

        # Log next scheduled trade
        next_run = schedule.next_run()
        logger.info(f"⏰ Next scheduled trade: {next_run}")

    def execute_scheduled_trade(self):
        """Execute the scheduled trade"""
        logger.info("⏰ Executing scheduled trade...")

        if not self.is_connected:
            logger.error("❌ Not connected to server - skipping trade")
            return

        if not self.is_authenticated:
            logger.error("❌ Not authenticated - skipping trade")
            return

        # Execute the trade
        self.create_market_buy_order()

        # Log next scheduled trade
        try:
            next_run = schedule.next_run()
            logger.info(f"⏰ Next scheduled trade: {next_run}")
        except:
            pass

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        def scheduler_thread():
            logger.info("🔄 Starting scheduler thread...")
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"❌ Scheduler error: {e}")
                    time.sleep(60)

        # Start scheduler in daemon thread
        scheduler_thread = Thread(target=scheduler_thread, daemon=True)
        scheduler_thread.start()

    def set_trading_parameters(self, symbol_name="EURUSD", volume=1000):
        """
        Set trading parameters

        Args:
            symbol_name (str): Symbol to trade (e.g., "EURUSD", "GBPUSD")
            volume (int): Position size in smallest units (1000 = 0.01 lots)
        """
        self.symbol_name = symbol_name
        self.volume = volume
        logger.info(f"📊 Trading parameters set: {symbol_name}, volume={volume}")


def main():
    """Main function to run the trading bot"""
    logger.info("🤖 Starting Scheduled Trading Bot")
    logger.info("=" * 50)

    # ⚠️ IMPORTANT CONFIGURATION ⚠️
    TRADE_TIME = "09:00"  # Time to execute daily trades (24-hour format)
    SYMBOL = "EURUSD"     # Trading symbol
    VOLUME = 1000         # Position size (1000 = 0.01 lots)

    logger.info(f"Configuration:")
    logger.info(f"  Trade Time: {TRADE_TIME}")
    logger.info(f"  Symbol: {SYMBOL}")
    logger.info(f"  Volume: {VOLUME} units ({VOLUME/100000:.2f} lots)")
    logger.info("=" * 50)

    try:
        # Create trader instance
        trader = ScheduledTrader()

        # Set trading parameters
        trader.set_trading_parameters(SYMBOL, VOLUME)

        # Schedule daily trades
        trader.schedule_daily_trade(TRADE_TIME)

        # Start scheduler in background
        trader.run_scheduler()

        # Start cTrader client
        trader.start_client()

        # Run Twisted reactor (this blocks)
        logger.info("🚀 Trading bot started! Press Ctrl+C to stop.")
        reactor.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down trading bot...")
        reactor.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        reactor.stop()


if __name__ == "__main__":
    main()