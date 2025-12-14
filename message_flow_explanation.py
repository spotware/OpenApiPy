#!/usr/bin/env python3
"""
Detailed Explanation: How cTrader Real-time Data Works

This demonstrates the complete message flow from subscription to receiving ticks
"""

import datetime
import logging
from twisted.internet import reactor

from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints

# Enhanced logging to show message flow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MessageFlowDemo:
    """Demonstrates the complete message flow for real-time data"""

    def __init__(self):
        self.client = None
        self.account_id = 5155500  # Example
        self.message_count = 0

        # Message type mapping for understanding
        self.message_types = {
            ProtoHeartbeatEvent().payloadType: "HeartbeatEvent",
            ProtoOAApplicationAuthRes().payloadType: "ApplicationAuthRes",
            ProtoOAAccountAuthRes().payloadType: "AccountAuthRes",
            ProtoOASymbolsListRes().payloadType: "SymbolsListRes",
            ProtoOASubscribeSpotsRes().payloadType: "SubscribeSpotsRes",
            ProtoOASpotEvent().payloadType: "SpotEvent",
            ProtoOAErrorRes().payloadType: "ErrorRes"
        }

    def setup_client(self):
        """Setup client with enhanced message tracking"""
        host = EndPoints.PROTOBUF_DEMO_HOST
        self.client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

        # This is the KEY callback - ALL messages come through here
        self.client.setMessageReceivedCallback(self.on_any_message_received)
        self.client.setConnectedCallback(self.on_connected)

    def on_any_message_received(self, client, message):
        """
        🔥 THIS IS THE CORE MECHANISM 🔥

        Every single message from the cTrader server comes through this callback.
        We check the message type to determine what kind of data it contains.
        """
        self.message_count += 1
        message_type_id = message.payloadType
        message_type_name = self.message_types.get(message_type_id, f"Unknown_{message_type_id}")

        logger.info(f"📨 Message #{self.message_count}: {message_type_name} (ID: {message_type_id})")

        # 🎯 THIS IS WHY WE CHECK FOR ProtoOASpotEvent
        if message_type_id == ProtoOASpotEvent().payloadType:
            logger.info("🔔 ⭐ TICK DATA DETECTED! ⭐")
            self.handle_tick_data(message)

        elif message_type_id == ProtoHeartbeatEvent().payloadType:
            # Heartbeats are sent every few seconds - ignore for clarity
            pass

        else:
            # Other message types (authentication, errors, etc.)
            self.handle_other_message(message, message_type_name)

    def handle_tick_data(self, message):
        """Handle the actual tick data from ProtoOASpotEvent"""
        try:
            # Extract the actual data from the Protocol Buffer message
            spot_data = Protobuf.extract(message)

            logger.info("📊 TICK DATA BREAKDOWN:")
            logger.info(f"   Symbol ID: {spot_data.symbolId}")
            logger.info(f"   Raw Bid: {spot_data.bid}")
            logger.info(f"   Raw Ask: {spot_data.ask}")

            # Convert from raw format to actual prices
            bid_price = spot_data.bid / 100000.0 if spot_data.bid else 0.0
            ask_price = spot_data.ask / 100000.0 if spot_data.ask else 0.0
            spread = ask_price - bid_price

            logger.info(f"   💰 Actual Bid: {bid_price:.5f}")
            logger.info(f"   💰 Actual Ask: {ask_price:.5f}")
            logger.info(f"   📏 Spread: {spread:.5f}")
            logger.info(f"   ⏰ Timestamp: {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

            # This is where your on_tick callback would be called
            logger.info("✅ This would trigger your on_tick() callback!")

        except Exception as e:
            logger.error(f"❌ Error processing tick data: {e}")

    def handle_other_message(self, message, message_type_name):
        """Handle non-tick messages"""
        try:
            if message_type_name != "HeartbeatEvent":
                data = Protobuf.extract(message)
                logger.info(f"📋 {message_type_name} received")

                # Show some details for important messages
                if hasattr(data, 'errorCode'):
                    logger.warning(f"   ⚠️  Error: {data.errorCode}")
                elif hasattr(data, 'symbol') and hasattr(data.symbol, '__len__'):
                    logger.info(f"   📊 Contains {len(data.symbol)} symbols")

        except Exception as e:
            logger.error(f"❌ Error processing {message_type_name}: {e}")

    def on_connected(self, client):
        """Connected to server - start the demonstration"""
        logger.info("🟢 CONNECTED TO SERVER")
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎯 DEMONSTRATION: How Real-time Data Works")
        logger.info("=" * 60)
        logger.info("")

        self.demonstrate_message_flow()

    def demonstrate_message_flow(self):
        """Demonstrate the complete message flow"""

        logger.info("📝 STEP 1: The Process Overview")
        logger.info("   1. Client sends ProtoOASubscribeSpotsReq")
        logger.info("   2. Server responds with ProtoOASubscribeSpotsRes (confirmation)")
        logger.info("   3. Server starts sending ProtoOASpotEvent messages")
        logger.info("   4. Each ProtoOASpotEvent = 1 tick (price update)")
        logger.info("   5. Your callback processes each tick")
        logger.info("")

        # Simulate the subscription process
        logger.info("📤 STEP 2: Sending Subscription Request...")
        logger.info("   → ProtoOASubscribeSpotsReq for EURUSD")
        logger.info("   → This tells server: 'Send me price updates for EURUSD'")
        logger.info("")

        logger.info("📥 STEP 3: What Happens Next...")
        logger.info("   → Server will send ProtoOASubscribeSpotsRes (confirmation)")
        logger.info("   → Then ProtoOASpotEvent messages start flowing")
        logger.info("   → Each ProtoOASpotEvent contains bid/ask prices")
        logger.info("   → Your on_tick callback gets called for each one")
        logger.info("")

        logger.info("🔄 STEP 4: Continuous Data Flow...")
        logger.info("   Market moves → Server detects change → ProtoOASpotEvent sent → Your callback triggered")
        logger.info("   This happens 100-1000+ times per minute for active symbols!")
        logger.info("")

        # Show the key insight
        logger.info("💡 KEY INSIGHT:")
        logger.info("   setMessageReceivedCallback() receives ALL messages")
        logger.info("   We check message.payloadType to identify ProtoOASpotEvent")
        logger.info("   ProtoOASpotEvent.payloadType = 2131 (this ID means 'tick data')")
        logger.info("   When we see payloadType == 2131, we know it's a price update!")
        logger.info("")

        logger.info("🎯 MONITORING MESSAGES...")
        logger.info("   Watch for ProtoOASpotEvent messages below...")
        logger.info("   (Note: You need to actually subscribe to see tick data)")
        logger.info("")

    def show_payload_type_mapping(self):
        """Show what different payload types mean"""
        logger.info("🔍 MESSAGE TYPE REFERENCE:")
        for payload_type_id, name in self.message_types.items():
            logger.info(f"   {payload_type_id:4d} = {name}")
        logger.info("")


def main():
    """Run the demonstration"""
    logger.info("🚀 Starting Message Flow Demonstration")
    logger.info("This will show you exactly how real-time data works")
    logger.info("")

    try:
        demo = MessageFlowDemo()
        demo.setup_client()
        demo.show_payload_type_mapping()

        # Start the client
        demo.client.startService()

        # Stop after 30 seconds for demo purposes
        def stop_demo():
            logger.info("")
            logger.info("⏹️  Demo completed!")
            logger.info("💡 Key Takeaway:")
            logger.info("   setMessageReceivedCallback() + payloadType checking = Real-time data")
            logger.info("   ProtoOASpotEvent (ID: 2131) = Tick data")
            logger.info("   Every price change triggers a new ProtoOASpotEvent message")
            reactor.stop()

        reactor.callLater(30, stop_demo)

        # Run the reactor
        reactor.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Demo stopped by user")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main()