#!/usr/bin/env python

from typing import Dict, List, Optional
from twisted.internet import defer
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api.protobuf import Protobuf
from ctrader_open_api import Client
import uuid
import time
from datetime import datetime, timedelta


class TradeClient:
    """
    High-level wrapper for cTrader Open API trading operations.
    Provides simplified methods for common trading tasks.
    """

    def __init__(self, client: Client, auth: Dict):
        """
        Initialize TradeClient with an existing Client instance.

        Args:
            client: An instance of ctrader_open_api.Client
            auth: Dictionary containing authentication credentials
        """
        self._client = client
        self._auth = auth
        self._account_id = auth.get("account_id")
        self._is_app_authorized = False
        self._is_account_authorized = False

        # Cache for synchronous methods
        self._positions_cache = []
        self._symbols_cache = {}
        self._last_positions_update = None
        self._last_symbols_update = None
        self._cache_timeout = 30  # 30 seconds cache timeout

    def execute_market_order(self, symbol_id, trade_side, volume, comment=None):
        """
        Execute a market order.

        Args:
            symbol_id (int): Symbol ID for the instrument
            trade_side (str): 'BUY' or 'SELL'
            volume (int): Volume in cents (e.g., 100000 for 0.01 lots)
            comment (str, optional): Order comment

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with order result
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self._account_id
        request.symbolId = symbol_id
        request.orderType = ProtoOAOrderType.MARKET
        request.tradeSide = ProtoOATradeSide.BUY if trade_side.upper() == 'BUY' else ProtoOATradeSide.SELL
        request.volume = volume

        if comment:
            request.comment = comment

        return self._client.send(request)

    def place_order(self, symbol_id, trade_side, volume, order_type="MARKET", price=None, stop_price=None, comment=None, label=None):
        """
        Place an order (market, limit, or stop).

        Args:
            symbol_id (int): Symbol ID for the instrument
            trade_side (str): 'BUY' or 'SELL'
            volume (int): Volume in cents (e.g., 100000 for 0.01 lots)
            order_type (str): 'MARKET', 'LIMIT', or 'STOP'
            price (float, optional): Price for limit/stop orders
            stop_price (float, optional): Stop price for stop orders
            comment (str, optional): Order comment
            label (str, optional): Order label

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with order result
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self._account_id
        request.symbolId = symbol_id
        request.tradeSide = ProtoOATradeSide.BUY if trade_side.upper() == 'BUY' else ProtoOATradeSide.SELL
        request.volume = volume

        # Set order type
        order_type = order_type.upper()
        if order_type == "MARKET":
            request.orderType = ProtoOAOrderType.MARKET
        elif order_type == "LIMIT":
            request.orderType = ProtoOAOrderType.LIMIT
            if price is None:
                return defer.fail(Exception("Price is required for limit orders"))
            request.limitPrice = int(price * 100000)  # Convert to pips
        elif order_type == "STOP":
            request.orderType = ProtoOAOrderType.STOP
            if price is None:
                return defer.fail(Exception("Price is required for stop orders"))
            request.stopPrice = int(price * 100000)  # Convert to pips
        else:
            return defer.fail(Exception(f"Invalid order type: {order_type}"))

        # Optional parameters
        if comment:
            request.comment = comment
        if label:
            request.label = label

        return self._client.send(request)

    def place_limit_order(self, symbol_id, trade_side, volume, price, comment=None, label=None):
        """
        Place a limit order.

        Args:
            symbol_id (int): Symbol ID for the instrument
            trade_side (str): 'BUY' or 'SELL'
            volume (int): Volume in cents (e.g., 100000 for 0.01 lots)
            price (float): Limit price
            comment (str, optional): Order comment
            label (str, optional): Order label

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with order result
        """
        return self.place_order(symbol_id, trade_side, volume, "LIMIT", price=price, comment=comment, label=label)

    def place_stop_order(self, symbol_id, trade_side, volume, price, comment=None, label=None):
        """
        Place a stop order.

        Args:
            symbol_id (int): Symbol ID for the instrument
            trade_side (str): 'BUY' or 'SELL'
            volume (int): Volume in cents (e.g., 100000 for 0.01 lots)
            price (float): Stop price
            comment (str, optional): Order comment
            label (str, optional): Order label

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with order result
        """
        return self.place_order(symbol_id, trade_side, volume, "STOP", price=price, comment=comment, label=label)

    def cancel_order(self, order_id):
        """
        Cancel a pending order.

        Args:
            order_id (int): Order ID to cancel

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with cancellation result
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOACancelOrderReq()
        request.ctidTraderAccountId = self._account_id
        request.orderId = order_id

        return self._client.send(request)

    def close_position(self, position_id, volume):
        """
        Close a position (partially or completely).

        Args:
            position_id (int): Position ID to close
            volume (int, optional): Volume to close in cents. If None, closes entire position.

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with close result
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOAClosePositionReq()
        request.ctidTraderAccountId = self._account_id
        request.positionId = position_id
        request.volume = volume

        return self._client.send(request)

    def get_account_net_profit(self):
        """
        Get account's net profit/loss.

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with account details
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOATraderReq()
        request.ctidTraderAccountId = self._account_id

        return self._client.send(request)

    def list_positions(self):
        """
        Get list of open positions.

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with positions list
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = self._account_id

        return self._client.send(request)

    def list_orders(self):
        """
        Get list of pending orders.
        Note: Orders are typically included in the reconcile response.

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with orders list
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = self._account_id

        return self._client.send(request)

    def list_symbols(self, include_archived=False):
        """
        Get list of available trading symbols.

        Args:
            include_archived (bool, optional): Whether to include archived symbols. Default: False

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves with symbols list
        """
        if not self._is_account_authorized:
            return defer.fail(Exception("Account not authenticated"))

        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self._account_id
        request.includeArchivedSymbols = include_archived

        return self._client.send(request)

    @property
    def is_authenticated(self):
        """Check if both app and account are authenticated."""
        return self._is_app_authorized and self._is_account_authorized

    @property
    def account_id(self):
        """Get the current account ID."""
        return self._account_id

    # Synchronous wrapper methods for RiskManager
    def get_positions_sync(self) -> List:
        """
        Get positions synchronously with caching.
        Returns a list of position objects, not a Deferred.
        """
        current_time = time.time()

        # Check if cache is valid
        if (self._last_positions_update and
            current_time - self._last_positions_update < self._cache_timeout):
            return self._positions_cache

        # Only update cache if we're authenticated and connected
        if self.is_authenticated and hasattr(self, '_client') and self._client.isConnected:
            # Update cache asynchronously but return immediately
            self._update_positions_cache()

        return self._positions_cache

    def get_symbols_sync(self) -> Dict:
        """
        Get symbols synchronously with caching.
        Returns a dictionary of symbol data, not a Deferred.
        """
        current_time = time.time()

        # Check if cache is valid
        if (self._last_symbols_update and
            current_time - self._last_symbols_update < self._cache_timeout):
            return self._symbols_cache

        # Only update cache if we're authenticated and connected
        if self.is_authenticated and hasattr(self, '_client') and self._client.isConnected:
            # Update cache asynchronously but return immediately
            self._update_symbols_cache()

        return self._symbols_cache

    def get_closed_profit_sync(self, time_delta: timedelta) -> float:
        """
        Get closed profit synchronously for the specified time period.
        Returns a float value, not a Deferred.
        """
        try:
            from twisted.internet import reactor
            current_time = datetime.now()
            from_timestamp = int((current_time - time_delta).timestamp() * 1000)
            to_timestamp = int(current_time.timestamp() * 1000)

            # Store result in instance variable
            self._sync_result = None
            self._sync_error = None
            self._sync_done = False

            def on_success(message):
                try:
                    deal_data = Protobuf.extract(message)
                    total_profit = 0.0

                    if hasattr(deal_data, 'deal'):
                        for deal in deal_data.deal:
                            if hasattr(deal, 'closePositionDetail') and deal.closePositionDetail:
                                gross_profit = deal.closePositionDetail.grossProfit / 100.0
                                commission = getattr(deal.closePositionDetail, 'commission', 0) / 100.0
                                swap = getattr(deal.closePositionDetail, 'swap', 0) / 100.0
                                net_profit = gross_profit - commission - swap
                                total_profit += net_profit

                    self._sync_result = total_profit
                    self._sync_done = True
                except Exception as e:
                    print(f"Error processing deal list: {e}")
                    self._sync_error = e
                    self._sync_done = True

            def on_error(failure):
                print(f"Error fetching deal history: {failure}")
                self._sync_error = failure
                self._sync_done = True

            # Make the request
            self._request_deal_history_sync(from_timestamp, to_timestamp, on_success, on_error)

            # Wait for completion with timeout
            timeout = 10.0  # 10 second timeout
            start_time = time.time()
            while not self._sync_done and (time.time() - start_time) < timeout:
                time.sleep(0.1)  # Small delay

            if self._sync_error:
                print(f"Deal history request failed: {self._sync_error}")
                return 0.0

            return self._sync_result if self._sync_result is not None else 0.0

        except Exception as e:
            print(f"Error in get_closed_profit_sync: {e}")
            return 0.0

    def _update_positions_cache(self):
        """Update positions cache asynchronously"""
        def on_positions(message):
            try:
                positions_data = Protobuf.extract(message)
                positions = []
                if hasattr(positions_data, 'position'):
                    positions = list(positions_data.position)

                self._positions_cache = positions
                self._last_positions_update = time.time()
                print(f"Updated positions cache: {len(positions)} positions")
            except Exception as e:
                print(f"Error updating positions cache: {e}")

        def on_error(failure):
            print(f"Error fetching positions: {failure}")
            # Don't spam errors if we already have cached data
            if not self._positions_cache:
                print("Warning: No positions data available")

        try:
            deferred = self.list_positions()
            deferred.addTimeout(20.0, self._client._runningReactor)  # 20 second timeout
            deferred.addCallback(on_positions)
            deferred.addErrback(on_error)
        except Exception as e:
            print(f"Error requesting positions update: {e}")

    def _update_symbols_cache(self):
        """Update symbols cache asynchronously"""
        def on_symbols(message):
            try:
                symbols_data = Protobuf.extract(message)
                symbols = {}
                if hasattr(symbols_data, 'symbol'):
                    for symbol in symbols_data.symbol:
                        symbols[symbol.symbolName.upper()] = {
                            'symbolId': symbol.symbolId,
                            'symbolName': symbol.symbolName,
                            'minVolume': symbol.minVolume if hasattr(symbol, 'minVolume') else 100000,
                        }

                self._symbols_cache = symbols
                self._last_symbols_update = time.time()
                print(f"Updated symbols cache: {len(symbols)} symbols")
            except Exception as e:
                print(f"Error updating symbols cache: {e}")

        def on_error(failure):
            print(f"Error fetching symbols: {failure}")
            # Don't spam errors if we already have cached data
            if not self._symbols_cache:
                print("Warning: No symbols data available")

        try:
            deferred = self.list_symbols()
            deferred.addTimeout(20.0, self._client._runningReactor)  # 20 second timeout
            deferred.addCallback(on_symbols)
            deferred.addErrback(on_error)
        except Exception as e:
            print(f"Error requesting symbols update: {e}")

    def _request_deal_history_sync(self, from_timestamp, to_timestamp, callback, errback):
        """Request deal history synchronously"""
        try:
            from twisted.internet import reactor

            request = ProtoOADealListReq()
            request.payloadType = ProtoOAPayloadType.PROTO_OA_DEAL_LIST_REQ
            request.ctidTraderAccountId = self._account_id
            request.fromTimestamp = from_timestamp
            request.toTimestamp = to_timestamp
            request.maxRows = 100

            deferred = self._client.send(request)
            deferred.addTimeout(25.0, reactor)  # 25 second timeout, longer than client default
            deferred.addCallback(callback)
            deferred.addErrback(errback)

        except Exception as e:
            print(f"Error requesting deal history: {e}")
            errback(e)