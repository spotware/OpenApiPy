#!/usr/bin/env python

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

    def __init__(self, client: Client):
        """
        Initialize TradeClient with an existing Client instance.

        Args:
            client: An instance of ctrader_open_api.Client
        """
        self._client = client
        self._account_id = None
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

    def close_position(self, position_id, volume=None):
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

        if volume is not None:
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

    @property
    def is_authenticated(self):
        """Check if both app and account are authenticated."""
        return self._is_app_authorized and self._is_account_authorized

    @property
    def account_id(self):
        """Get the current account ID."""
        return self._account_id