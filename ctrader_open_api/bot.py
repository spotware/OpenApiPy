#!/usr/bin/env python
"""
Modern Bot framework using async/await instead of Twisted.
Provides event-driven callbacks for tick and bar data with a clean interface.
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any

from ctrader_open_api.client import Client
from ctrader_open_api.trade_client import TradeClient
from ctrader_open_api.endpoints import EndPoints
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api.protobuf import Protobuf


logger = logging.getLogger(__name__)


class Bot:
    """
    Modern high-level bot framework for cTrader Open API.
    Provides event-driven callbacks for tick and bar data using async/await.
    """

    def __init__(
        self,
        auth: Dict,
        host_type: str = "demo",
        max_messages_per_second: int = 5,
        auto_authenticate: bool = True
    ):
        """
        Initialize Bot with async client.

        Args:
            auth: Dictionary containing authentication credentials
            host_type: 'demo' or 'live' for server selection
            max_messages_per_second: Rate limit for outgoing messages
            auto_authenticate: Whether to authenticate automatically on connection
        """
        # Select appropriate host
        if host_type.lower() == "live":
            host = EndPoints.PROTOBUF_LIVE_HOST
        else:
            host = EndPoints.PROTOBUF_DEMO_HOST

        self.auth = auth
        self.host_type = host_type
        self.auto_authenticate = auto_authenticate

        # Create modern client
        self.client = Client(
            host=host,
            port=EndPoints.PROTOBUF_PORT,
            max_messages_per_second=max_messages_per_second
        )

        # Create trade client
        self.trade_client = TradeClient(self.client, auth)

        # Setup event handlers
        self._setup_event_handlers()

        # Internal state
        self.is_running = False
        self.main_task: Optional[asyncio.Task] = None

    def _setup_event_handlers(self):
        """Setup event handlers for client events."""
        # Connection events
        self.client.add_connection_callback(self._on_client_connected)
        self.client.add_disconnection_callback(self._on_client_disconnected)

        # Message events
        self.client.add_message_handler(
            ProtoOASpotEvent().payloadType,
            self._on_spot_event_received
        )

        self.client.add_message_handler(
            ProtoOAGetTrendbarsRes().payloadType,
            self._on_trendbar_event_received
        )

        self.client.add_message_handler(
            ProtoOAExecutionEvent().payloadType,
            self._on_execution_event_received
        )

    async def start(self):
        """
        Start the bot by connecting to the server and running the event loop.
        """
        logger.info("Starting modern bot...")
        self.is_running = True

        try:
            # Connect to server
            if not await self.client.connect():
                logger.error("Failed to connect to server")
                return False

            logger.info("Bot started successfully")

            # Keep the bot running
            while self.is_running:
                await asyncio.sleep(1)

            return True

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error in bot: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """
        Stop the bot and disconnect from server.
        """
        logger.info("Stopping bot...")
        self.is_running = False

        await self.client.disconnect()
        logger.info("Bot stopped")

    # Event Handlers (Override these in your bot implementation)

    async def on_connected(self):
        """
        Called when bot connects to cTrader server.
        Override this method in your bot implementation.
        """
        logger.info("Bot connected to cTrader server")

        if self.auto_authenticate:
            logger.info("Authenticating...")
            success = await self.trade_client.authenticate()
            if success:
                logger.info("Authentication successful")
            else:
                logger.error("Authentication failed")

    async def on_disconnected(self, reason: str):
        """
        Called when bot disconnects from cTrader server.
        Override this method in your bot implementation.

        Args:
            reason: Disconnection reason
        """
        logger.info(f"Bot disconnected: {reason}")

    async def on_tick(self, spot_event=None):
        """
        Called when tick data is received.
        Override this method in your bot implementation.

        Args:
            spot_event: ProtoOASpotEvent message containing tick data
        """
        if spot_event:
            # Display useful tick information
            logger.debug(f"📈 Tick received - Symbol ID: {spot_event.symbolId}")
            if hasattr(spot_event, 'bid') and hasattr(spot_event, 'ask'):
                bid_price = spot_event.bid / 1e5
                ask_price = spot_event.ask / 1e5
                logger.debug(f"   Bid: {bid_price:.5f}, Ask: {ask_price:.5f}")
            if hasattr(spot_event, 'timestamp'):
                logger.debug(f"   Timestamp: {spot_event.timestamp}")
        else:
            logger.debug("on_tick - no data")

    async def on_bar(self, trendbar_response=None):
        """
        Called when bar data is received.
        Override this method in your bot implementation.

        Args:
            trendbar_response: ProtoOAGetTrendbarsRes message containing bar data
        """
        logger.debug("on_bar")

    async def on_execution(self, execution_event=None):
        """
        Called when execution events are received (orders/positions).
        Override this method in your bot implementation.

        Args:
            execution_event: ProtoOAExecutionEvent message
        """
        if execution_event:
            logger.info(f"Execution event: {execution_event}")

    async def on_message(self, message):
        """
        Called for all received messages.
        Override this method to handle custom message processing.

        Args:
            message: Raw protobuf message
        """
        # Default: do nothing
        pass

    # Internal Event Handlers

    async def _on_client_connected(self, client):
        """Internal callback for client connection."""
        await self.on_connected()

    async def _on_client_disconnected(self, client, reason):
        """Internal callback for client disconnection."""
        await self.on_disconnected(reason)

    async def _on_spot_event_received(self, message):
        """Internal callback for spot events."""
        spot_event = Protobuf.extract(message)
        await self.on_tick(spot_event)

    async def _on_trendbar_event_received(self, message):
        """Internal callback for trendbar events."""
        trendbar_response = Protobuf.extract(message)
        await self.on_bar(trendbar_response)

    async def _on_execution_event_received(self, message):
        """Internal callback for execution events."""
        execution_event = Protobuf.extract(message)
        await self.on_execution(execution_event)

    # Convenience methods for common operations

    async def subscribe_to_spots(
        self,
        symbol_id: int,
        include_timestamp: bool = True
    ) -> bool:
        """
        Subscribe to spot (tick) data for a symbol.

        Args:
            symbol_id: Symbol ID to subscribe to
            include_timestamp: Include timestamp in tick data

        Returns:
            bool: True if subscription successful, False otherwise
        """
        try:
            if not self.trade_client.is_authenticated:
                logger.error("Must authenticate before subscribing to data")
                return False

            response = await self.trade_client.subscribe_to_spots(
                symbol_id, include_timestamp
            )

            if response:
                logger.info(f"✅ Successfully subscribed to symbol {symbol_id} tick data")
                return True
            else:
                logger.error(f"❌ Failed to subscribe to symbol {symbol_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to symbol {symbol_id}: {e}")
            return False

    async def get_trendbars(
        self,
        symbol_id: int,
        period: int,
        count: int = 1000,
        timeout: int = 15
    ):
        """
        Request historical bar data.

        Args:
            symbol_id: Symbol ID
            period: Bar period (e.g., ProtoOATrendbarPeriod.M1)
            count: Number of bars to retrieve
            timeout: Request timeout in seconds

        Returns:
            Trendbar response or None if failed
        """
        try:
            if not self.trade_client.is_authenticated:
                raise Exception("Must authenticate before requesting data")

            request = ProtoOAGetTrendbarsReq()
            request.ctidTraderAccountId = self.trade_client.account_id
            request.symbolId = symbol_id
            request.period = period
            request.count = count

            return await self.client.send_message(request, timeout=timeout)

        except Exception as e:
            logger.error(f"Error getting trendbars: {e}")
            return None

    # Helper methods

    async def find_symbol_by_name(self, symbol_name: str) -> Optional[Dict]:
        """
        Find symbol information by name.

        Args:
            symbol_name: Symbol name (e.g., "EURUSD")

        Returns:
            Symbol information dict or None if not found
        """
        symbols = await self.trade_client.get_symbols()
        return symbols.get(symbol_name.upper())

    async def wait_for_authentication(self, timeout: int = 30) -> bool:
        """
        Wait for authentication to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if authenticated, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        while not self.trade_client.is_authenticated:
            if asyncio.get_event_loop().time() - start_time > timeout:
                return False
            await asyncio.sleep(0.1)
        return True

    # Properties

    @property
    def is_authenticated(self) -> bool:
        """Check if bot is authenticated."""
        return self.trade_client.is_authenticated

    @property
    def is_connected(self) -> bool:
        """Check if bot is connected to server."""
        return self.client.is_connected

    @property
    def account_id(self) -> int:
        """Get the account ID."""
        return self.trade_client.account_id


# Utility function to run a bot
async def run_bot(bot_class, auth: Dict, **kwargs):
    """
    Utility function to run a bot with proper error handling.

    Args:
        bot_class: Bot class to instantiate
        auth: Authentication credentials
        **kwargs: Additional arguments for bot constructor
    """
    bot = bot_class(auth, **kwargs)
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        if bot.is_running:
            await bot.stop()


def run_bot_sync(bot_class, auth: Dict, **kwargs):
    """
    Synchronous wrapper to run a bot (for backwards compatibility).

    Args:
        bot_class: Bot class to instantiate
        auth: Authentication credentials
        **kwargs: Additional arguments for bot constructor
    """
    asyncio.run(run_bot(bot_class, auth, **kwargs))


if __name__ == "__main__":
    auth = {
        "client_id": "7870_AGNoUDByyfLOPTiKMGwZHQbK5whzvUNo2BpTCsTXff3ajFz8my",
        "client_secret": "0xtJwsbjTul1lmjjOI5rwSaViVIhcMJNqW8bWNzARwHVwQdeuA",
        "account_id": 45416297,
        "account_token": "-KwZawTvJbMvSGaPaQ-Rrt96CltxaiCsWAEK_6IuSDE",
    }
    run_bot_sync(Bot, auth)