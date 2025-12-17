#!/usr/bin/env python


from typing import Dict
import logging
from ctrader_open_api import Client, TcpProtocol, EndPoints
from ctrader_open_api.trade_client import TradeClient
from ctrader_open_api.protobuf import Protobuf
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from twisted.internet import reactor


class Bot:
    """
    High-level bot framework for cTrader Open API.
    Provides event-driven callbacks for tick and bar data.
    """

    def __init__(
            self,
            auth: Dict,
            host_type="demo"):
        """
        Initialize Bot with TradeClient instance.

        Args:
            host_type (str): 'demo' or 'live' for server selection
        """
        # Select appropriate host based on type
        if host_type.lower() == "live":
            host = EndPoints.PROTOBUF_LIVE_HOST
        else:
            host = EndPoints.PROTOBUF_DEMO_HOST

        self.auth = auth

        # Create client instance
        self._client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

        # Initialize TradeClient with the client
        self.trade_client = TradeClient(self._client, auth)

        # Set up event callbacks
        self._client._connectedCallback = self._on_connected
        self._client._disconnectedCallback = self._on_disconnected
        self._client._messageReceivedCallback = self._on_message_received

        # Internal state
        self._is_running = False

    def start(self):
        """
        Start the bot by invoking client.startService() and reactor.
        """
        print("Starting bot...")
        self._is_running = True
        self._client.startService()

        # Only run reactor if it's not already running
        if not reactor.running:
            reactor.run()

    def stop(self):
        """
        Stop the bot and client service.
        """
        print("Stopping bot...")
        self._is_running = False
        if self._client.running:
            self._client.stopService()

        # Stop reactor if it's running
        if reactor.running:
            reactor.stop()

    def _on_connected(self, client):
        """Internal callback for client connection."""
        print("Bot connected to cTrader server")
        self.on_connected()

    def _on_disconnected(self, client, reason):
        """Internal callback for client disconnection."""
        print(f"Bot disconnected from cTrader server: {reason}")
        self.on_disconnected(reason)

    def _on_message_received(self, client, message):
        """Internal callback for processing incoming messages."""
        # Filter out heartbeat messages (payloadType 51)
        if message.payloadType == 51:  # ProtoHeartbeatEvent
            return

        # Handle different message types
        if message.payloadType == ProtoOASpotEvent().payloadType:
            # Tick data received
            spot_event = Protobuf.extract(message)
            self.on_tick(spot_event)

        elif message.payloadType == ProtoOAGetTrendbarsRes().payloadType:
            # Bar data received
            trendbar_response = Protobuf.extract(message)
            self.on_bar(trendbar_response)

        else:
            # Handle other message types (but not heartbeats)
            self.on_message(message)

    # Override these methods in your bot implementation
    def on_connected(self):
        """
        Called when bot connects to cTrader server.
        Override this method in your bot implementation.
        """
        print("Authenticating...")
        self._auth()

    def on_disconnected(self, reason):
        """
        Called when bot disconnects from cTrader server.
        Override this method in your bot implementation.

        Args:
            reason: Disconnection reason
        """
        print("on_disconnected")

    def on_tick(self, spot_event=None):
        """
        Called when tick data is received.
        Override this method in your bot implementation.

        Args:
            spot_event: ProtoOASpotEvent message containing tick data
        """
        if spot_event:
            # Display useful tick information
            print(f"📈 Tick received - Symbol ID: {spot_event.symbolId}")
            if hasattr(spot_event, 'bid') and hasattr(spot_event, 'ask'):
                print(f"   Bid: {spot_event.bid/1e5:.5f}, Ask: {spot_event.ask/1e5:.5f}")
            if hasattr(spot_event, 'timestamp'):
                print(f"   Timestamp: {spot_event.timestamp}")
        else:
            print("on_tick - no data")

    def on_bar(self, trendbar_response=None):
        """
        Called when bar data is received.
        Override this method in your bot implementation.

        Args:
            trendbar_response: ProtoOAGetTrendbarsRes message containing bar data
        """
        print("on_bar")

    def on_message(self, message):
        """
        Called for all received messages.
        Override this method to handle custom message processing.

        Args:
            message: Raw protobuf message
        """
        pass
        # message_content = Protobuf.extract(message)
        # print(f"type: {message.payloadType} message content:", str(message_content))

    # Convenience methods for common operations
    def subscribe_to_spots(self, symbol_id, timeout_seconds=3600):
        """
        Subscribe to spot (tick) data for a symbol.

        Args:
            symbol_id (int): Symbol ID to subscribe to
            timeout_seconds (int): Subscription timeout in seconds

        Returns:
            twisted.internet.defer.Deferred: Promise for subscription result
        """
        if not self.trade_client.is_authenticated:
            raise Exception("Must authenticate before subscribing to data")

        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = self.trade_client.account_id
        request.symbolId.append(symbol_id)
        request.subscribeToSpotTimestamp = True

        return self._client.send(request)

    def get_trendbars(self, symbol_id, period, count=1000):
        """
        Request historical bar data.

        Args:
            symbol_id (int): Symbol ID
            period (ProtoOATrendbarPeriod): Bar period (e.g., ProtoOATrendbarPeriod.M1)
            count (int): Number of bars to retrieve

        Returns:
            twisted.internet.defer.Deferred: Promise for bar data
        """
        if not self.trade_client.is_authenticated:
            raise Exception("Must authenticate before requesting data")

        request = ProtoOAGetTrendbarsReq()
        request.ctidTraderAccountId = self.trade_client.account_id
        request.symbolId = symbol_id
        request.period = period
        request.count = count

        return self._client.send(request)


    def _auth(self):
        """
        Perform application and account authentication.

        Args:
            client_id (str): Application client ID
            secret (str): Application client secret
            account_id (int): Account ID for trading
            account_token (str): Account access token

        Returns:
            twisted.internet.defer.Deferred: Promise that resolves when auth is complete
        """

        account_id = self.auth.get("account_id")
        account_token = self.auth.get("account_token")
        client_id = self.auth.get("client_id")
        secret = self.auth.get("client_secret")

        def on_app_auth_response(message):
            """Handle application auth response"""
            if message.payloadType == ProtoOAApplicationAuthRes().payloadType:
                self.trade_client._is_app_authorized = True
                print("Application authenticated successfully")

                # Now perform account authentication
                account_request = ProtoOAAccountAuthReq()
                account_request.ctidTraderAccountId = account_id
                account_request.accessToken = account_token

                account_deferred = self._client.send(account_request)
                account_deferred.addCallback(on_account_auth_response)
                account_deferred.addErrback(on_auth_error)
            else:
                print("Application authentication failed - unexpected response type")

        def on_account_auth_response(message):
            """Handle account auth response"""
            if message.payloadType == ProtoOAAccountAuthRes().payloadType:
                self.trade_client._is_account_authorized = True
                self.trade_client._account_id = account_id
                print(f"Account {account_id} authenticated successfully")
            else:
                print("Account authentication failed - unexpected response type")
            
            # # This is a test for place limit order.
            # self.trade_client.place_limit_order(
            #     symbol_id=41,  # XAUUSD
            #     trade_side='BUY',
            #     price=4200/1e5,
            #     volume=100  # 0.01 lots
            # ).addCallback(lambda result: print("Market order executed:", result)
            # ).addErrback(lambda error: print("Error executing market order:", error)
            # )

            self.trade_client.list_symbols().addCallback(print_symbols)

            # Subscribe to ticks after authentication is complete
            self.subscribe_to_ticks("XAUUSD", True)
        def print_symbols(result):
            symbols = Protobuf.extract(result)
            for s in symbols.symbol:
                if "XAUUSD" in s.symbolName:
                    print(s)

        def on_auth_error(failure):
            """Handle authentication errors"""
            print(f"Authentication error: {failure}")

        # First perform application authentication
        app_request = ProtoOAApplicationAuthReq()
        app_request.clientId = client_id
        app_request.clientSecret = secret

        app_deferred = self._client.send(app_request)
        app_deferred.addCallback(on_app_auth_response)
        app_deferred.addErrback(on_auth_error)

    @property
    def is_running(self):
        """Check if bot is currently running."""
        return self._is_running

    @property
    def is_connected(self):
        """Check if bot is connected to cTrader server."""
        return self._client.isConnected
    
    def on_tick_subscription_success(self, result, symbol_id: int, symbol_name: str):
        """Tick subscription successful"""
        print(f"✅ Successfully subscribed to {symbol_name} tick data")

    def subscribe_to_ticks(self, symbol_name: str, subscribe_to_timestamp: bool = True):
        """
        Subscribe to tick data for a symbol

        Args:
            symbol_name (str): Symbol name (e.g., "EURUSD")
            subscribe_to_timestamp (bool): Include timestamp in tick data
        """

        print(f"📊 Subscribing to {symbol_name} tick data...")

        symbol_id = 41  # hard code

        try:
            request = ProtoOASubscribeSpotsReq()
            request.ctidTraderAccountId = self.auth.get("account_id")
            request.symbolId.append(symbol_id)
            request.subscribeToSpotTimestamp = subscribe_to_timestamp

            deferred = self._client.send(request)
            deferred.addCallbacks(
                lambda result, sym_id=symbol_id, sym_name=symbol_name: self.on_tick_subscription_success(result, sym_id, sym_name),
                # self.on_error
            )

            return True

        except Exception as e:
            print(f"❌ Failed to subscribe to {symbol_name} ticks: {e}")
            return False