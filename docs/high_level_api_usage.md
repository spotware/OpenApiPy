# High-Level API Usage Guide

This document explains how to use the new high-level `TradeClient` and `Bot` classes that were implemented according to the specifications in `docs/specs/spec.md`.

## Overview

The high-level API provides two main classes:

1. **`TradeClient`** - Simplified wrapper for common trading operations
2. **`Bot`** - Event-driven bot framework with automatic callbacks

These classes sit on top of the existing low-level cTrader Open API implementation, providing a more user-friendly interface for common trading tasks.

## TradeClient Class

### Basic Usage

```python
from ctrader_open_api import Client, TradeClient, TcpProtocol, EndPoints

# Create client instance
client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

# Initialize TradeClient with existing client instance (as specified)
trade_client = TradeClient(client)
```

### Authentication

```python
# Authenticate with simplified method (handles both app and account auth)
auth_deferred = trade_client.auth(
    client_id="your_client_id",
    secret="your_client_secret",
    account_id=12345678,
    account_token="your_access_token"
)

auth_deferred.addCallback(lambda result: print("Authenticated!"))
auth_deferred.addErrback(lambda error: print(f"Auth error: {error}"))
```

### Trading Operations

#### Execute Market Order
```python
order_deferred = trade_client.execute_market_order(
    symbol_id=1,        # EURUSD
    trade_side='BUY',   # or 'SELL'
    volume=100000,      # 0.01 lots (volume in cents)
    comment="My order"  # optional
)
```

#### Close Position
```python
# Close entire position
close_deferred = trade_client.close_position(position_id=123456)

# Close partial position
close_deferred = trade_client.close_position(position_id=123456, volume=50000)
```

#### Get Account Information
```python
profit_deferred = trade_client.get_account_net_profit()
positions_deferred = trade_client.list_positions()
orders_deferred = trade_client.list_orders()
```

## Bot Class

### Basic Usage

```python
from ctrader_open_api import Bot

class MyBot(Bot):
    def __init__(self):
        # Initialize with TradeClient instance (as specified)
        super().__init__(host_type="demo")  # or "live"

    def on_connected(self):
        """Called when bot connects"""
        print("Bot connected!")
        # Perform authentication here

    def on_tick(self, spot_event=None):
        """Called when tick data is received"""
        print("Received tick data")
        if spot_event:
            print(f"Bid: {spot_event.bid}, Ask: {spot_event.ask}")

    def on_bar(self, trendbar_response=None):
        """Called when bar data is received"""
        print("Received bar data")

    def on_disconnected(self, reason):
        """Called when bot disconnects"""
        print(f"Disconnected: {reason}")

# Create and start bot
bot = MyBot()
bot.start()  # Invokes client.startService() as specified
```

### Complete Bot Example

```python
class TradingBot(Bot):
    def __init__(self):
        super().__init__(host_type="demo")
        self.is_authenticated = False

        # Your credentials
        self.credentials = {
            "ClientId": "your_client_id",
            "Secret": "your_client_secret",
            "AccountId": 12345678,
            "AccessToken": "your_access_token"
        }

    def on_connected(self):
        """Authenticate when connected"""
        auth_deferred = self.trade_client.auth(
            self.credentials["ClientId"],
            self.credentials["Secret"],
            self.credentials["AccountId"],
            self.credentials["AccessToken"]
        )
        auth_deferred.addCallback(self._on_authenticated)

    def _on_authenticated(self, result):
        """Handle successful authentication"""
        self.is_authenticated = True
        print("Bot authenticated!")

        # Subscribe to tick data for EURUSD
        self.subscribe_to_spots(symbol_id=1, timeout_seconds=3600)

    def on_tick(self, spot_event=None):
        """Process incoming tick data"""
        if self.is_authenticated and spot_event:
            # Your trading logic here
            if spot_event.bid > some_condition:
                # Execute trade
                self.trade_client.execute_market_order(
                    symbol_id=spot_event.symbolId,
                    trade_side='BUY',
                    volume=100000
                )
```

## Key Features

### TradeClient Features
- ✅ Accepts existing Client instance (as specified)
- ✅ Simplified authentication (handles both app and account auth)
- ✅ Market order execution
- ✅ Position closing
- ✅ Account profit/loss retrieval
- ✅ Position and order listing
- ✅ Built on Twisted deferreds for async operations

### Bot Features
- ✅ Initializes TradeClient instance automatically
- ✅ `start()` method invokes `client.startService()` (as specified)
- ✅ Event-driven callbacks (`on_tick`, `on_bar`)
- ✅ Connection/disconnection handling
- ✅ Convenient methods for data subscription
- ✅ Easy to extend with custom trading logic

## Error Handling

Both classes use Twisted deferreds for asynchronous operations. Handle errors using `.addErrback()`:

```python
def on_error(failure):
    print(f"Error: {failure}")

trade_client.auth(...).addErrback(on_error)
```

## Requirements

- All existing dependencies (Twisted, protobuf, etc.)
- The implementation is fully compatible with the existing cTrader Open API infrastructure

## Migration from Low-Level API

If you're currently using the low-level API, you can easily migrate:

**Before (Low-level):**
```python
client = Client(...)
request = ProtoOAApplicationAuthReq()
request.clientId = client_id
request.clientSecret = secret
client.send(request)
```

**After (High-level):**
```python
trade_client = TradeClient(client)
trade_client.auth(client_id, secret, account_id, token)
```

The high-level API provides the same functionality with much less boilerplate code, while still giving you access to the underlying client for advanced operations when needed.