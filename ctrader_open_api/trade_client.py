#!/usr/bin/env python

from typing import Dict
from twisted.internet import defer
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from ctrader_open_api.protobuf import Protobuf
from ctrader_open_api import Client
import uuid


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