#!/usr/bin/env python3
"""
XAUUSD Risk Management System
Continuously monitors and closes all XAUUSD positions

This is a long-running program that:
1. Connects to cTrader Open API
2. Continuously scans all open positions
3. Automatically closes any XAUUSD positions found
4. Provides comprehensive logging and error handling

IMPORTANT WARNINGS:
- This will close ALL XAUUSD positions immediately
- Test thoroughly with demo account first
- Ensure you understand the implications before running on live account

Author: Claude Code Assistant
"""

import datetime
import time
import json
import logging
from threading import Thread, Event
from twisted.internet import reactor, task, threads
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
        logging.FileHandler('xauusd_risk_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XAUUSDRiskManager:
    def __init__(self, credentials_file="credentials.json", scan_interval=30):
        """
        Initialize the XAUUSD Risk Manager

        Args:
            credentials_file (str): Path to credentials JSON file
            scan_interval (int): How often to scan for positions (seconds)
        """
        self.credentials_file = credentials_file
        self.scan_interval = scan_interval
        self.credentials = None
        self.client = None
        self.account_id = None
        self.target_symbol = "XAUUSD"
        self.target_symbol_id = None
        self.is_authenticated = False
        self.is_connected = False
        self.is_scanning = False
        self.stop_event = Event()

        # Statistics
        self.total_positions_closed = 0
        self.total_scans_performed = 0
        self.last_scan_time = None

        # Load credentials and setup client
        self.load_credentials()
        self.setup_client()

    def load_credentials(self):
        """Load cTrader API credentials from JSON file"""
        try:
            with open(self.credentials_file, 'r') as f:
                self.credentials = json.load(f)
            self.account_id = self.credentials["AccountId"]
            logger.info(f"📋 Loaded credentials for account: {self.account_id}")
        except Exception as e:
            logger.error(f"❌ Failed to load credentials: {e}")
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
                logger.info("🔧 Using demo account")

            # Create client
            self.client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

            # Set callbacks
            self.client.setConnectedCallback(self.on_connected)
            self.client.setDisconnectedCallback(self.on_disconnected)
            self.client.setMessageReceivedCallback(self.on_message_received)

        except Exception as e:
            logger.error(f"❌ Failed to setup client: {e}")
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
        self.is_scanning = False

    def on_message_received(self, client, message):
        """Callback for all received messages"""
        # Filter out common messages to reduce log noise
        if message.payloadType not in [ProtoHeartbeatEvent().payloadType]:
            logger.debug(f"📨 Received message type: {message.payloadType}")

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

        # Step 3: Get symbols list to find XAUUSD symbol ID
        self.get_symbols_list()

    def get_symbols_list(self):
        """Step 3: Get list of available symbols to find XAUUSD symbol ID"""
        logger.info(f"📋 Getting symbols list to find {self.target_symbol}...")

        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.account_id
        request.includeArchivedSymbols = False

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_symbols_received, self.on_error)

    def on_symbols_received(self, result):
        """Symbols list received"""
        symbols = Protobuf.extract(result)

        # Find XAUUSD symbol
        matching_symbols = [s for s in symbols.symbol if s.symbolName == self.target_symbol]

        if not matching_symbols:
            logger.warning(f"⚠️  Symbol '{self.target_symbol}' not found in account")
            logger.info("📋 Available symbols include:")
            for symbol in symbols.symbol[:10]:  # Show first 10 symbols
                logger.info(f"   - {symbol.symbolName}")
            self.target_symbol_id = None
        else:
            self.target_symbol_id = matching_symbols[0].symbolId
            logger.info(f"✅ Found {self.target_symbol} with symbol ID: {self.target_symbol_id}")

        # Start the scanning process
        logger.info("🚀 Risk manager is ready!")
        self.start_scanning()

    def start_scanning(self):
        """Start the continuous position scanning"""
        if self.is_scanning:
            logger.warning("⚠️  Scanning already in progress")
            return

        self.is_scanning = True
        logger.info(f"🔍 Starting continuous scanning every {self.scan_interval} seconds")
        logger.info(f"🎯 Target: Close all {self.target_symbol} positions")

        # Start the scanning loop
        self.schedule_next_scan()

    def schedule_next_scan(self):
        """Schedule the next position scan"""
        if self.stop_event.is_set():
            return

        # Schedule next scan
        reactor.callLater(self.scan_interval, self.perform_scan)

    def perform_scan(self):
        """Perform a single scan of all positions"""
        if not self.is_connected or not self.is_authenticated:
            logger.warning("⚠️  Not connected/authenticated - skipping scan")
            self.schedule_next_scan()
            return

        self.total_scans_performed += 1
        self.last_scan_time = datetime.datetime.now()

        logger.info(f"🔍 Performing scan #{self.total_scans_performed} at {self.last_scan_time.strftime('%H:%M:%S')}")

        # Request current positions via reconcile
        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = self.account_id

        deferred = self.client.send(request)
        deferred.addCallbacks(self.on_positions_received, self.on_scan_error)

    def on_positions_received(self, result):
        """Process received positions and close XAUUSD positions"""
        try:
            positions_data = Protobuf.extract(result)

            # Count total positions
            total_positions = len(positions_data.position) if hasattr(positions_data, 'position') else 0
            logger.info(f"📊 Found {total_positions} open positions")

            if total_positions == 0:
                logger.info("✅ No open positions found")
                self.schedule_next_scan()
                return

            # Check each position
            xauusd_positions = []
            for position in positions_data.position:
                try:
                    symbol_id = position.tradeData.symbolId
                    position_id = position.positionId
                    volume = position.tradeData.volume
                    trade_side = "BUY" if position.tradeData.tradeSide == ProtoOATradeSide.BUY else "SELL"

                    # Check if this is our target symbol (XAUUSD)
                    is_target_symbol = False
                    if self.target_symbol_id and symbol_id == self.target_symbol_id:
                        is_target_symbol = True

                    logger.debug(f"📍 Position ID {position_id}: Symbol ID {symbol_id}, {trade_side}, Volume {volume}")

                    if is_target_symbol:
                        xauusd_positions.append({
                            'position_id': position_id,
                            'symbol_id': symbol_id,
                            'volume': volume,
                            'trade_side': trade_side,
                            'position': position
                        })
                        logger.info(f"🎯 Found {self.target_symbol} position: ID {position_id}, {trade_side}, Volume {volume}")

                except Exception as e:
                    logger.error(f"❌ Error processing position: {e}")

            # Close all XAUUSD positions
            if xauusd_positions:
                logger.warning(f"🚨 Closing {len(xauusd_positions)} {self.target_symbol} position(s)")
                for pos_data in xauusd_positions:
                    self.close_position(pos_data)
            else:
                logger.info(f"✅ No {self.target_symbol} positions found")

            # Schedule next scan
            self.schedule_next_scan()

        except Exception as e:
            logger.error(f"❌ Error processing positions: {e}")
            self.schedule_next_scan()

    def close_position(self, position_data):
        """Close a specific position"""
        position_id = position_data['position_id']
        volume = position_data['volume']
        trade_side = position_data['trade_side']

        logger.info(f"❌ Closing {self.target_symbol} position {position_id} ({trade_side}, {volume} units)")

        try:
            request = ProtoOAClosePositionReq()
            request.ctidTraderAccountId = self.account_id
            request.positionId = position_id
            request.volume = volume  # Close entire position

            deferred = self.client.send(request)
            deferred.addCallbacks(
                lambda result, pos_id=position_id: self.on_position_closed(result, pos_id),
                lambda failure, pos_id=position_id: self.on_close_position_error(failure, pos_id)
            )

        except Exception as e:
            logger.error(f"❌ Failed to close position {position_id}: {e}")

    def on_position_closed(self, result, position_id):
        """Position successfully closed"""
        self.total_positions_closed += 1
        logger.info(f"✅ Successfully closed {self.target_symbol} position {position_id}")
        logger.info(f"📊 Total positions closed: {self.total_positions_closed}")

    def on_close_position_error(self, failure, position_id):
        """Error closing position"""
        logger.error(f"❌ Failed to close position {position_id}: {failure}")

    def on_scan_error(self, failure):
        """Error during position scan"""
        logger.error(f"❌ Position scan failed: {failure}")
        # Continue scanning despite errors
        self.schedule_next_scan()

    def on_error(self, failure):
        """General error callback"""
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

    def stop_scanning(self):
        """Stop the scanning process"""
        logger.info("⏹️  Stopping position scanning...")
        self.stop_event.set()
        self.is_scanning = False

    def get_statistics(self):
        """Get current statistics"""
        return {
            'total_scans_performed': self.total_scans_performed,
            'total_positions_closed': self.total_positions_closed,
            'last_scan_time': self.last_scan_time,
            'is_scanning': self.is_scanning,
            'is_connected': self.is_connected,
            'is_authenticated': self.is_authenticated,
            'target_symbol': self.target_symbol,
            'scan_interval': self.scan_interval
        }

    def log_statistics(self):
        """Log current statistics"""
        stats = self.get_statistics()
        logger.info("📊 Risk Manager Statistics:")
        logger.info(f"   Target Symbol: {stats['target_symbol']}")
        logger.info(f"   Scan Interval: {stats['scan_interval']} seconds")
        logger.info(f"   Total Scans: {stats['total_scans_performed']}")
        logger.info(f"   Positions Closed: {stats['total_positions_closed']}")
        logger.info(f"   Last Scan: {stats['last_scan_time']}")
        logger.info(f"   Status: {'🟢 Active' if stats['is_scanning'] else '🔴 Inactive'}")


def main():
    """Main function to run the risk manager"""
    logger.info("🛡️  Starting XAUUSD Risk Management System")
    logger.info("=" * 60)

    # ⚠️ IMPORTANT CONFIGURATION ⚠️
    TARGET_SYMBOL = "XAUUSD"       # Symbol to monitor and close
    SCAN_INTERVAL = 30             # Scan every 30 seconds

    logger.info(f"Configuration:")
    logger.info(f"  Target Symbol: {TARGET_SYMBOL}")
    logger.info(f"  Scan Interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 60)

    logger.warning("🚨 THIS WILL CLOSE ALL XAUUSD POSITIONS AUTOMATICALLY!")
    logger.warning("🚨 MAKE SURE YOU UNDERSTAND THE IMPLICATIONS!")
    logger.warning("🚨 TEST WITH DEMO ACCOUNT FIRST!")
    logger.info("=" * 60)

    try:
        # Create risk manager instance
        risk_manager = XAUUSDRiskManager(scan_interval=SCAN_INTERVAL)

        # Start client
        risk_manager.start_client()

        # Setup statistics logging every 5 minutes
        def log_stats():
            risk_manager.log_statistics()
            reactor.callLater(300, log_stats)  # Log every 5 minutes

        reactor.callLater(60, log_stats)  # Start after 1 minute

        # Run Twisted reactor (this blocks)
        logger.info("🚀 Risk manager started! Press Ctrl+C to stop.")
        logger.info("🔍 Scanning for XAUUSD positions will begin after authentication...")
        reactor.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down risk manager...")
        if 'risk_manager' in locals():
            risk_manager.stop_scanning()
        reactor.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        reactor.stop()


if __name__ == "__main__":
    main()