# How Tick Data Works: Complete Flow Explanation

You asked a great question about why we check for `ProtoOASpotEvent`. Here's the complete explanation of how real-time data flows from the market to your callback.

## 🤔 Your Question
> "So the general idea is that I use setMessageReceivedCallback. so whenever there is a message from the server, it will be checked if it is ProtoOASpotEvent event (Why)? If so , it means a new tick? I don't quite follow"

## ✅ **Correct Understanding**
You've got it right! Here's exactly what happens:

## 📡 **The Complete Message Flow**

```
Real Market Price Change
         ↓
cTrader Server Detects Change
         ↓
Server Creates ProtoOASpotEvent Message
         ↓
Message Sent Over Network
         ↓
Your Client Receives Message
         ↓
setMessageReceivedCallback() Triggered
         ↓
You Check: message.payloadType == ProtoOASpotEvent().payloadType?
         ↓
If YES → Extract bid/ask prices → Call your on_tick()
If NO  → Handle other message types
```

## 🔍 **Why Check for ProtoOASpotEvent?**

### The Server Sends MANY Different Message Types:
```python
# Different message types from server:
ProtoHeartbeatEvent         # Server ping (every few seconds)
ProtoOAApplicationAuthRes   # Authentication response
ProtoOAAccountAuthRes       # Account auth response
ProtoOASymbolsListRes       # List of available symbols
ProtoOASubscribeSpotsRes    # Subscription confirmation
ProtoOASpotEvent           # 🎯 TICK DATA (price updates)
ProtoOAErrorRes            # Error messages
ProtoOAExecutionEvent      # Trade execution updates
# ... and many more
```

### ProtoOASpotEvent = Tick Data
- **`ProtoOASpotEvent`** is the **ONLY** message type that contains real-time price updates
- **Every time the market price changes**, the server sends a `ProtoOASpotEvent`
- **Payload Type ID: 2131** uniquely identifies this message type

## 📊 **Visual Example**

### What Actually Happens:
```
09:30:15.123 → EURUSD bid/ask changes to 1.08245/1.08247
                ↓
              Server sends: ProtoOASpotEvent {
                payloadType: 2131,
                symbolId: 1,
                bid: 108245,      // Raw format (multiply by 100000)
                ask: 108247,      // Raw format
                timestamp: 1642334215123
              }
                ↓
              Your callback receives this message
                ↓
              You check: if (message.payloadType == 2131) → "This is tick data!"
                ↓
              Extract: bid = 108245/100000 = 1.08245
                ↓
              Call: on_tick(TickData(symbol="EURUSD", bid=1.08245, ask=1.08247))
```

## 🔄 **The Subscription Process**

### Step 1: Subscribe to Real-time Data
```python
# You send this request:
request = ProtoOASubscribeSpotsReq()
request.symbolId.append(eurusd_symbol_id)  # Subscribe to EURUSD
client.send(request)
```

### Step 2: Server Confirms Subscription
```python
# Server responds with:
ProtoOASubscribeSpotsRes {
  payloadType: 2134,  // Different ID - this is confirmation, not tick data
  ctidTraderAccountId: 5155500
}
```

### Step 3: Real-time Data Starts Flowing
```python
# Now server continuously sends:
ProtoOASpotEvent { bid: 108245, ask: 108247 }  // Tick 1
ProtoOASpotEvent { bid: 108246, ask: 108248 }  // Tick 2
ProtoOASpotEvent { bid: 108244, ask: 108246 }  // Tick 3
ProtoOASpotEvent { bid: 108245, ask: 108247 }  // Tick 4
# ... continues forever (until you unsubscribe)
```

## 💡 **Code Breakdown**

### The Universal Message Handler:
```python
def on_message_received(self, client, message):
    """ALL messages from server come through here"""

    # Check what type of message this is
    message_type = message.payloadType

    # Different message types:
    if message_type == ProtoOASpotEvent().payloadType:           # 2131
        # 🎯 THIS IS TICK DATA
        self.handle_tick_data(message)

    elif message_type == ProtoHeartbeatEvent().payloadType:      # 51
        # Server heartbeat - ignore
        pass

    elif message_type == ProtoOAErrorRes().payloadType:          # 2124
        # Error message
        self.handle_error(message)

    # ... handle other message types
```

### Processing the Tick Data:
```python
def handle_tick_data(self, message):
    """Extract actual prices from ProtoOASpotEvent"""

    # Convert Protocol Buffer to Python object
    spot_data = Protobuf.extract(message)

    # Extract the actual data
    symbol_id = spot_data.symbolId      # Which symbol this price is for
    raw_bid = spot_data.bid             # Raw bid price
    raw_ask = spot_data.ask             # Raw ask price

    # Convert from cTrader's raw format to decimal
    bid_price = raw_bid / 100000.0      # 108245 → 1.08245
    ask_price = raw_ask / 100000.0      # 108247 → 1.08247

    # Create your tick data structure
    tick = TickData(
        symbol_name="EURUSD",
        bid=bid_price,
        ask=ask_price,
        timestamp=datetime.datetime.now()
    )

    # Call your callback
    if self.on_tick_callback:
        self.on_tick_callback(tick)     # 🎯 This triggers your on_tick function!
```

## 📈 **Frequency & Volume**

### How Often Do You Get ProtoOASpotEvent?
- **Major pairs (EURUSD)**: 100-1000+ per minute during active hours
- **Minor pairs (AUDCAD)**: 50-200 per minute
- **Exotic pairs (USDTRY)**: 10-100 per minute
- **Commodities (XAUUSD)**: 200-500 per minute

### Each Message = One Tick
```python
# In 1 minute, you might receive:
ProtoOASpotEvent  # Tick 1: 1.08245/1.08247
ProtoOASpotEvent  # Tick 2: 1.08246/1.08248
ProtoOASpotEvent  # Tick 3: 1.08244/1.08246
# ... 200 more messages
ProtoOASpotEvent  # Tick 203: 1.08250/1.08252
```

## 🎯 **Key Insights**

### 1. **One Message Type = One Data Type**
- `ProtoOASpotEvent` (ID: 2131) = Tick data ONLY
- Other message types contain different data
- You MUST check the message type to know what data it contains

### 2. **The Server Pushes Data to You**
- You don't request each tick individually
- After subscribing, server automatically sends updates
- Each price change = new `ProtoOASpotEvent` message

### 3. **All Messages Through One Callback**
- `setMessageReceivedCallback()` receives EVERYTHING
- Heartbeats, errors, confirmations, tick data - all come through here
- You filter by `payloadType` to find what you want

### 4. **Why This Design?**
- **Efficiency**: One network connection handles all data types
- **Reliability**: Server controls when to send updates
- **Flexibility**: You can subscribe to multiple symbols simultaneously

## 🚀 **Practical Usage**

### Simple Tick Counter:
```python
def on_message_received(self, client, message):
    if message.payloadType == ProtoOASpotEvent().payloadType:
        self.tick_count += 1
        if self.tick_count % 100 == 0:
            print(f"Received {self.tick_count} ticks!")
```

### Multi-Symbol Handler:
```python
def on_message_received(self, client, message):
    if message.payloadType == ProtoOASpotEvent().payloadType:
        spot_data = Protobuf.extract(message)
        symbol_name = self.symbol_ids[spot_data.symbolId]  # Convert ID to name

        print(f"Tick for {symbol_name}: {spot_data.bid/100000:.5f}/{spot_data.ask/100000:.5f}")
```

## 🔧 **Testing the Flow**

Run the `message_flow_explanation.py` script to see this in action:

```bash
python message_flow_explanation.py
```

You'll see output like:
```
📨 Message #1: ApplicationAuthRes (ID: 2122)
📨 Message #2: AccountAuthRes (ID: 2123)
📨 Message #3: SymbolsListRes (ID: 2127)
📨 Message #4: HeartbeatEvent (ID: 51)
📨 Message #5: SpotEvent (ID: 2131)
🔔 ⭐ TICK DATA DETECTED! ⭐
📊 TICK DATA BREAKDOWN:
   💰 Actual Bid: 1.08245
   💰 Actual Ask: 1.08247
✅ This would trigger your on_tick() callback!
```

## 🎉 **Summary**

**Your understanding is 100% correct!**

1. **`setMessageReceivedCallback()`** receives ALL server messages
2. **We check `message.payloadType`** to identify message types
3. **`ProtoOASpotEvent` (ID: 2131)** means "tick data"
4. **Each `ProtoOASpotEvent`** = one price update = one tick
5. **We extract bid/ask prices** and call your `on_tick()` callback

The beauty of this system is that **every price change in the real market** automatically becomes a **Python function call** in your code! 🚀