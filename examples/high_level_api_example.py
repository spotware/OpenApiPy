#!/usr/bin/env python
"""
Example demonstrating the high-level TradeClient and Bot API
as specified in docs/specs/spec.md
"""

from ctrader_open_api import Client, TradeClient, Bot, TcpProtocol, EndPoints
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from twisted.internet import reactor, defer
import uuid


# Example 1: Using TradeClient directly
def example_trade_client():
    """Example showing direct use of TradeClient class"""

    # Create client instance (as specified in the docs)
    client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

    # Initialize TradeClient with existing client instance
    trade_client = TradeClient(client)

    # Credentials (replace with your actual credentials)
    credentials = {
        "ClientId": "your_client_id",
        "Secret": "your_client_secret",
        "AccountId": 12345678,
        "AccessToken": "your_access_token"
    }

    def on_connected(client):
        print("Connected to cTrader")

        # Authenticate using the simplified auth method
        auth_deferred = trade_client.auth(
            credentials["ClientId"],
            credentials["Secret"],
            credentials["AccountId"],
            credentials["AccessToken"]
        )

        auth_deferred.addCallback(on_authenticated)
        auth_deferred.addErrback(on_error)

    def on_authenticated(result):
        print("Authentication successful!")

        # Example: Execute a market order
        order_deferred = trade_client.execute_market_order(
            symbol_id=1,  # EURUSD
            trade_side='BUY',
            volume=100000,  # 0.01 lots
            comment="Test order"
        )
        order_deferred.addCallback(on_order_executed)
        order_deferred.addErrback(on_error)

        # Example: Get account net profit
        profit_deferred = trade_client.get_account_net_profit()
        profit_deferred.addCallback(on_profit_received)
        profit_deferred.addErrback(on_error)

        # Example: List positions
        positions_deferred = trade_client.list_positions()
        positions_deferred.addCallback(on_positions_received)
        positions_deferred.addErrback(on_error)

    def on_order_executed(result):
        print("Order executed:", result)

    def on_profit_received(result):
        print("Account profit/loss:", result)

    def on_positions_received(result):
        print("Open positions:", result)

        # If you want to close a position (example)
        # close_deferred = trade_client.close_position(position_id=123456)
        # close_deferred.addCallback(lambda r: print("Position closed:", r))

    def on_error(failure):
        print("Error:", failure)

    def on_disconnected(client, reason):
        print("Disconnected:", reason)

    # Set up client callbacks
    client._connectedCallback = on_connected
    client._disconnectedCallback = on_disconnected

    # Start the client
    client.startService()
    reactor.run()


# Example 2: Using Bot class (as specified in the docs)
class MyBot(Bot):
    """Custom bot implementation following the specification"""

    def __init__(self):
        # Initialize with TradeClient instance (as specified)
        super().__init__(host_type="demo")

        # Your bot's state variables
        self.is_authenticated = False

        # Credentials (replace with your actual credentials)
        self.credentials = {
            "ClientId": "your_client_id",
            "Secret": "your_client_secret",
            "AccountId": 12345678,
            "AccessToken": "your_access_token"
        }

    def on_connected(self):
        """Called when bot connects (overrides base class)"""
        print("MyBot connected!")

        # Authenticate when connected
        auth_deferred = self.trade_client.auth(
            self.credentials["ClientId"],
            self.credentials["Secret"],
            self.credentials["AccountId"],
            self.credentials["AccessToken"]
        )

        auth_deferred.addCallback(self._on_authenticated)
        auth_deferred.addErrback(self._on_error)

    def _on_authenticated(self, result):
        """Handle successful authentication"""
        self.is_authenticated = True
        print("MyBot authenticated successfully!")

        # Subscribe to tick data for EURUSD
        self.subscribe_to_spots(symbol_id=1, timeout_seconds=3600)

    def on_tick(self, spot_event=None):
        """Called when tick data is received (overrides base class)"""
        print("MyBot received tick data")
        if spot_event:
            # Process tick data here
            print(f"Tick for symbol {spot_event.symbolId}: Bid={spot_event.bid}, Ask={spot_event.ask}")

            # Example trading logic
            if self.is_authenticated:
                # Simple example: place buy order if bid price meets criteria
                # This is just an example - implement your own logic
                pass

    def on_bar(self, trendbar_response=None):
        """Called when bar data is received (overrides base class)"""
        print("MyBot received bar data")
        if trendbar_response:
            # Process bar data here
            print(f"Received {len(trendbar_response.trendbar)} bars")

    def on_disconnected(self, reason):
        """Called when bot disconnects"""
        print(f"MyBot disconnected: {reason}")
        self.is_authenticated = False

    def _on_error(self, failure):
        """Handle errors"""
        print("MyBot error:", failure)


def example_bot():
    """Example showing how to use the Bot class"""

    # Create and start bot
    bot = MyBot()

    # start() invokes client.startService() as specified
    bot.start()


if __name__ == "__main__":
    print("Choose example to run:")
    print("1. TradeClient direct usage")
    print("2. Bot class usage")

    choice = input("Enter choice (1 or 2): ")

    if choice == "1":
        example_trade_client()
    elif choice == "2":
        example_bot()
    else:
        print("Invalid choice")