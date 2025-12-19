#!/usr/bin/env python
"""
Modern TradeClient using the new async client.
Provides a clean async/await interface for trading operations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ctrader_open_api.client import Client
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api.protobuf import Protobuf


logger = logging.getLogger(__name__)


class TradeClient:
    """
    Modern high-level wrapper for cTrader Open API trading operations.
    Provides async/await methods for common trading tasks.
    """

    def __init__(self, client: Client, auth: Dict):
        """
        Initialize TradeClient with a Client instance.

        Args:
            client: An instance of Client
            auth: Dictionary containing authentication credentials
        """
        self.client = client
        self.auth = auth
        self.account_id = auth.get("account_id")
        self.is_app_authorized = False
        self.is_account_authorized = False

        # Cache for data
        self.positions_cache: List = []
        self.symbols_cache: Dict = {}
        self.last_positions_update: Optional[float] = None
        self.last_symbols_update: Optional[float] = None
        self.cache_timeout = 30  # 30 seconds

        # Setup event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers for real-time updates."""
        # Handle execution events (order/position updates)
        self.client.add_message_handler(
            ProtoOAExecutionEvent().payloadType,
            self._handle_execution_event
        )

        # Handle spot events (tick data)
        self.client.add_message_handler(
            ProtoOASpotEvent().payloadType,
            self._handle_spot_event
        )

    async def authenticate(self) -> bool:
        """
        Perform application and account authentication.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Step 1: Application authentication
            app_auth_req = ProtoOAApplicationAuthReq()
            app_auth_req.clientId = self.auth["client_id"]
            app_auth_req.clientSecret = self.auth["client_secret"]

            logger.info("Authenticating application...")
            app_response = await self.client.send_message(app_auth_req)

            if not app_response or app_response.payloadType != ProtoOAApplicationAuthRes().payloadType:
                logger.error("Application authentication failed")
                return False

            self.is_app_authorized = True
            logger.info("Application authenticated successfully")

            # Step 2: Account authentication
            account_auth_req = ProtoOAAccountAuthReq()
            account_auth_req.ctidTraderAccountId = self.account_id
            account_auth_req.accessToken = self.auth["account_token"]

            logger.info(f"Authenticating account {self.account_id}...")
            account_response = await self.client.send_message(account_auth_req)

            if not account_response or account_response.payloadType != ProtoOAAccountAuthRes().payloadType:
                logger.error("Account authentication failed")
                return False

            self.is_account_authorized = True
            logger.info(f"Account {self.account_id} authenticated successfully")

            # Initialize data caches
            await self._initialize_caches()

            return True

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    async def _initialize_caches(self):
        """Initialize data caches after authentication."""
        try:
            # Load symbols
            await self.update_symbols_cache()

            # Load positions
            await self.update_positions_cache()

        except Exception as e:
            logger.error(f"Error initializing caches: {e}")

    # Trading Operations

    async def execute_market_order(
        self,
        symbol_id: int,
        trade_side: str,
        volume: int,
        comment: Optional[str] = None,
        timeout: int = 10
    ) -> Any:
        """
        Execute a market order.

        Args:
            symbol_id: Symbol ID for the instrument
            trade_side: 'BUY' or 'SELL'
            volume: Volume in cents (e.g., 100000 for 0.01 lots)
            comment: Optional order comment
            timeout: Request timeout in seconds

        Returns:
            Order execution response or None if failed
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self.account_id
        request.symbolId = symbol_id
        request.orderType = ProtoOAOrderType.MARKET
        request.tradeSide = ProtoOATradeSide.BUY if trade_side.upper() == 'BUY' else ProtoOATradeSide.SELL
        request.volume = volume

        if comment:
            request.comment = comment

        logger.info(f"Executing {trade_side} market order for symbol {symbol_id}, volume {volume}")
        return await self.client.send_message(request, timeout=timeout)

    async def place_limit_order(
        self,
        symbol_id: int,
        trade_side: str,
        volume: int,
        price: float,
        comment: Optional[str] = None,
        label: Optional[str] = None,
        timeout: int = 10
    ) -> Any:
        """
        Place a limit order.

        Args:
            symbol_id: Symbol ID for the instrument
            trade_side: 'BUY' or 'SELL'
            volume: Volume in cents (e.g., 100000 for 0.01 lots)
            price: Limit price
            comment: Optional order comment
            label: Optional order label
            timeout: Request timeout in seconds

        Returns:
            Order placement response or None if failed
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self.account_id
        request.symbolId = symbol_id
        request.orderType = ProtoOAOrderType.LIMIT
        request.tradeSide = ProtoOATradeSide.BUY if trade_side.upper() == 'BUY' else ProtoOATradeSide.SELL
        request.volume = volume
        request.limitPrice = int(price * 100000)  # Convert to pips

        if comment:
            request.comment = comment
        if label:
            request.label = label

        logger.info(f"Placing {trade_side} limit order for symbol {symbol_id}, volume {volume}, price {price}")
        return await self.client.send_message(request, timeout=timeout)

    async def close_position(self, position_id: int, volume: int, timeout: int = 10) -> Any:
        """
        Close a position (partially or completely).

        Args:
            position_id: Position ID to close
            volume: Volume to close in cents
            timeout: Request timeout in seconds

        Returns:
            Close position response or None if failed
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOAClosePositionReq()
        request.ctidTraderAccountId = self.account_id
        request.positionId = position_id
        request.volume = volume

        logger.info(f"Closing position {position_id}, volume {volume}")
        return await self.client.send_message(request, timeout=timeout)

    async def cancel_order(self, order_id: int, timeout: int = 10) -> Any:
        """
        Cancel a pending order.

        Args:
            order_id: Order ID to cancel
            timeout: Request timeout in seconds

        Returns:
            Cancel order response or None if failed
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOACancelOrderReq()
        request.ctidTraderAccountId = self.account_id
        request.orderId = order_id

        logger.info(f"Cancelling order {order_id}")
        return await self.client.send_message(request, timeout=timeout)

    # Data Operations

    async def get_positions(self, timeout: int = 15) -> List:
        """
        Get list of open positions.

        Args:
            timeout: Request timeout in seconds

        Returns:
            List of position objects
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = self.account_id

        response = await self.client.send_message(request, timeout=timeout)
        if response:
            positions_data = Protobuf.extract(response)
            positions = list(positions_data.position) if hasattr(positions_data, 'position') else []

            # Update cache
            self.positions_cache = positions
            self.last_positions_update = time.time()

            logger.info(f"Retrieved {len(positions)} positions")
            return positions
        return []

    async def get_symbols(self, include_archived: bool = False, timeout: int = 15) -> Dict:
        """
        Get list of available trading symbols.

        Args:
            include_archived: Whether to include archived symbols
            timeout: Request timeout in seconds

        Returns:
            Dictionary of symbol data
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.account_id
        request.includeArchivedSymbols = include_archived

        response = await self.client.send_message(request, timeout=timeout)
        if response:
            symbols_data = Protobuf.extract(response)
            symbols = {}

            if hasattr(symbols_data, 'symbol'):
                for symbol in symbols_data.symbol:
                    symbols[symbol.symbolName.upper()] = {
                        'symbolId': symbol.symbolId,
                        'symbolName': symbol.symbolName,
                        'minVolume': symbol.minVolume if hasattr(symbol, 'minVolume') else 100000,
                    }

            # Update cache
            self.symbols_cache = symbols
            self.last_symbols_update = time.time()

            logger.info(f"Retrieved {len(symbols)} symbols")
            return symbols
        return {}

    async def get_deal_history(
        self,
        from_timestamp: int,
        to_timestamp: int,
        max_rows: int = 100,
        timeout: int = 20
    ) -> List:
        """
        Get deal history for the specified time period.

        Args:
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            max_rows: Maximum number of deals to retrieve
            timeout: Request timeout in seconds

        Returns:
            List of deal objects
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOADealListReq()
        request.payloadType = ProtoOAPayloadType.PROTO_OA_DEAL_LIST_REQ
        request.ctidTraderAccountId = self.account_id
        request.fromTimestamp = from_timestamp
        request.toTimestamp = to_timestamp
        request.maxRows = max_rows

        response = await self.client.send_message(request, timeout=timeout)
        if response:
            deal_data = Protobuf.extract(response)
            deals = list(deal_data.deal) if hasattr(deal_data, 'deal') else []
            logger.info(f"Retrieved {len(deals)} deals")
            return deals
        return []

    async def get_deals(
        self,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        max_rows: int = 1000,
        timeout: int = 20
    ) -> List:
        """
        Get list of deals (executed trades).

        Args:
            from_timestamp: Start timestamp in milliseconds (optional)
            to_timestamp: End timestamp in milliseconds (optional)
            max_rows: Maximum number of deals to retrieve
            timeout: Request timeout in seconds

        Returns:
            List of deal objects (ProtoOADeal)
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        # If no timestamps provided, get deals from last 30 days
        if from_timestamp is None or to_timestamp is None:
            from datetime import datetime, timedelta
            current_time = datetime.now()
            if to_timestamp is None:
                to_timestamp = int(current_time.timestamp() * 1000)
            if from_timestamp is None:
                from_timestamp = int((current_time - timedelta(days=30)).timestamp() * 1000)

        request = ProtoOADealListReq()
        request.payloadType = ProtoOAPayloadType.PROTO_OA_DEAL_LIST_REQ
        request.ctidTraderAccountId = self.account_id
        request.fromTimestamp = from_timestamp
        request.toTimestamp = to_timestamp
        request.maxRows = max_rows

        response = await self.client.send_message(request, timeout=timeout)
        if response:
            deal_data = Protobuf.extract(response)
            deals = list(deal_data.deal) if hasattr(deal_data, 'deal') else []
            logger.info(f"Retrieved {len(deals)} deals")
            return deals
        return []

    async def get_orders(self, timeout: int = 15) -> List:
        """
        Get list of pending orders.

        Args:
            timeout: Request timeout in seconds

        Returns:
            List of order objects
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = self.account_id

        response = await self.client.send_message(request, timeout=timeout)
        if response:
            reconcile_data = Protobuf.extract(response)
            orders = list(reconcile_data.order) if hasattr(reconcile_data, 'order') else []
            logger.info(f"Retrieved {len(orders)} orders")
            return orders
        return []

    # Cache Management

    async def update_positions_cache(self):
        """Update positions cache."""
        try:
            positions = await self.get_positions()
            logger.debug(f"Positions cache updated: {len(positions)} positions")
        except Exception as e:
            logger.error(f"Error updating positions cache: {e}")

    async def update_symbols_cache(self):
        """Update symbols cache."""
        try:
            symbols = await self.get_symbols()
            logger.debug(f"Symbols cache updated: {len(symbols)} symbols")
        except Exception as e:
            logger.error(f"Error updating symbols cache: {e}")

    def get_positions_cached(self) -> List:
        """
        Get positions from cache (synchronous).
        Updates cache if expired.
        """
        current_time = time.time()

        # Check if cache is valid
        if (self.last_positions_update and
            current_time - self.last_positions_update < self.cache_timeout):
            return self.positions_cache

        # Trigger async update if possible
        if self.is_authenticated:
            asyncio.create_task(self.update_positions_cache())

        return self.positions_cache

    def get_symbols_cached(self) -> Dict:
        """
        Get symbols from cache (synchronous).
        Updates cache if expired.
        """
        current_time = time.time()

        # Check if cache is valid
        if (self.last_symbols_update and
            current_time - self.last_symbols_update < self.cache_timeout):
            return self.symbols_cache

        # Trigger async update if possible
        if self.is_authenticated:
            asyncio.create_task(self.update_symbols_cache())

        return self.symbols_cache

    async def calculate_closed_profit(self, time_delta: timedelta) -> float:
        """
        Calculate closed profit for the specified time period.

        Args:
            time_delta: Time period to calculate profit for

        Returns:
            Total closed profit
        """
        try:
            current_time = datetime.now()
            from_timestamp = int((current_time - time_delta).timestamp() * 1000)
            to_timestamp = int(current_time.timestamp() * 1000)

            deals = await self.get_deal_history(from_timestamp, to_timestamp)

            total_profit = 0.0
            for deal in deals:
                if hasattr(deal, 'closePositionDetail') and deal.closePositionDetail:
                    gross_profit = deal.closePositionDetail.grossProfit / 100.0
                    commission = getattr(deal.closePositionDetail, 'commission', 0) / 100.0
                    swap = getattr(deal.closePositionDetail, 'swap', 0) / 100.0
                    net_profit = gross_profit - commission - swap
                    total_profit += net_profit

            return total_profit

        except Exception as e:
            logger.error(f"Error calculating closed profit: {e}")
            return 0.0

    # Market Data Subscriptions

    async def subscribe_to_spots(self, symbol_id: int, include_timestamp: bool = True, timeout: int = 10):
        """
        Subscribe to spot (tick) data for a symbol.

        Args:
            symbol_id: Symbol ID to subscribe to
            include_timestamp: Include timestamp in tick data
            timeout: Request timeout in seconds
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = self.account_id
        request.symbolId.append(symbol_id)
        request.subscribeToSpotTimestamp = include_timestamp

        logger.info(f"Subscribing to spots for symbol {symbol_id}")
        return await self.client.send_message(request, timeout=timeout)

    async def unsubscribe_from_spots(self, symbol_id: int, timeout: int = 10):
        """
        Unsubscribe from spot data for a symbol.

        Args:
            symbol_id: Symbol ID to unsubscribe from
            timeout: Request timeout in seconds
        """
        if not self.is_authenticated:
            raise Exception("Account not authenticated")

        request = ProtoOAUnsubscribeSpotsReq()
        request.ctidTraderAccountId = self.account_id
        request.symbolId.append(symbol_id)

        logger.info(f"Unsubscribing from spots for symbol {symbol_id}")
        return await self.client.send_message(request, timeout=timeout)

    # Event Handlers

    async def _handle_execution_event(self, message):
        """Handle execution events (order/position updates)."""
        try:
            execution_data = Protobuf.extract(message)
            logger.info(f"Execution event: {execution_data}")

            # Update positions cache when positions change
            if hasattr(execution_data, 'position'):
                asyncio.create_task(self.update_positions_cache())

        except Exception as e:
            logger.error(f"Error handling execution event: {e}")

    async def _handle_spot_event(self, message):
        """Handle spot events (tick data)."""
        try:
            spot_data = Protobuf.extract(message)
            # This will be handled by the bot's on_tick method
            # Just log for debugging
            logger.debug(f"Spot event for symbol {spot_data.symbolId}")

        except Exception as e:
            logger.error(f"Error handling spot event: {e}")

    # Properties

    @property
    def is_authenticated(self) -> bool:
        """Check if both app and account are authenticated."""
        return self.is_app_authorized and self.is_account_authorized

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.client.is_connected