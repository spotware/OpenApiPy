# Market Data Callbacks Guide (on_tick & on_bar)

This guide shows you how to implement real-time market data callbacks (`on_tick` and `on_bar`) using the cTrader Open API for algorithmic trading and market analysis.

## 🚀 Quick Start

### Basic Usage
```python
from market_data_handler import MarketDataHandler, TickData, BarData

# Create handler
handler = MarketDataHandler()

# Define callback functions
def my_on_tick(tick: TickData):
    print(f"TICK: {tick.symbol_name} Bid:{tick.bid:.5f} Ask:{tick.ask:.5f}")

def my_on_bar(bar: BarData):
    print(f"BAR: {bar.symbol_name} OHLC: {bar.open_price:.5f}/{bar.high_price:.5f}/{bar.low_price:.5f}/{bar.close_price:.5f}")

# Set callbacks
handler.set_on_tick_callback(my_on_tick)
handler.set_on_bar_callback(my_on_bar)

# Start and subscribe
handler.start()
# After authentication:
handler.subscribe_to_ticks("EURUSD")
handler.subscribe_to_bars("EURUSD", "M1")
```

## 📊 Data Structures

### TickData Structure
```python
@dataclass
class TickData:
    symbol_id: int              # Internal symbol ID
    symbol_name: str            # Symbol name (e.g., "EURUSD")
    bid: float                  # Bid price
    ask: float                  # Ask price
    spread: float               # Ask - Bid
    timestamp: datetime         # When tick occurred
    raw_timestamp: int          # Raw timestamp (milliseconds)

    @property
    def mid_price(self) -> float:  # (bid + ask) / 2
```

### BarData Structure
```python
@dataclass
class BarData:
    symbol_id: int              # Internal symbol ID
    symbol_name: str            # Symbol name
    period: str                 # Period (M1, H1, D1, etc.)
    open_time: datetime         # Bar open time
    open_price: float           # Open price
    high_price: float           # High price
    low_price: float            # Low price
    close_price: float          # Close price
    volume: int                 # Volume
    timestamp: datetime         # When bar was received

    @property
    def body_size(self) -> float:     # |close - open|
    @property
    def upper_shadow(self) -> float:  # High - max(open,close)
    @property
    def lower_shadow(self) -> float:  # Min(open,close) - low
    @property
    def is_bullish(self) -> bool:     # close > open
```

## 🔔 Callback Implementation

### Tick Data Callbacks (Real-time Price Updates)

```python
def on_tick_callback(tick: TickData):
    """Called for every price update (bid/ask change)"""

    # Basic price monitoring
    print(f"📊 {tick.symbol_name}: {tick.bid:.5f} / {tick.ask:.5f}")

    # Spread analysis
    if tick.spread > 0.0002:  # 2 pips for EURUSD
        print(f"⚠️  Wide spread detected: {tick.spread:.5f}")

    # Price alerts
    if tick.symbol_name == "EURUSD" and tick.mid_price > 1.1000:
        print("🚨 EURUSD above 1.1000!")

    # Store for analysis
    price_history.append((tick.timestamp, tick.mid_price))

    # Real-time trading decisions
    if should_buy(tick):
        place_buy_order(tick.symbol_name, tick.ask)
```

### Bar Data Callbacks (Candlestick Completion)

```python
def on_bar_callback(bar: BarData):
    """Called when a new candlestick/bar completes"""

    # Basic OHLC monitoring
    direction = "🟢 BULL" if bar.is_bullish else "🔴 BEAR"
    print(f"📈 {bar.symbol_name} {bar.period} {direction}")
    print(f"   OHLC: {bar.open_price:.5f}/{bar.high_price:.5f}/{bar.low_price:.5f}/{bar.close_price:.5f}")

    # Pattern recognition
    if bar.is_doji():  # You'd implement this
        print("🎯 Doji pattern detected")

    # Technical indicators
    if len(price_history) >= 20:
        sma_20 = calculate_sma(price_history, 20)
        if bar.close_price > sma_20:
            print("📈 Price above 20-period SMA")

    # Volume analysis
    if bar.volume > average_volume * 2:
        print(f"📊 High volume: {bar.volume}")

    # Multi-timeframe analysis
    update_higher_timeframe_data(bar)
```

## 🎯 Practical Examples

### 1. Simple Price Alert System
```python
class PriceAlerts:
    def __init__(self):
        self.alerts = {
            "EURUSD": {"above": 1.1000, "below": 1.0800},
            "GBPUSD": {"above": 1.2500, "below": 1.2000}
        }

    def on_tick(self, tick: TickData):
        if tick.symbol_name in self.alerts:
            alert = self.alerts[tick.symbol_name]

            if tick.mid_price > alert["above"]:
                print(f"🚨 {tick.symbol_name} ABOVE {alert['above']}: {tick.mid_price:.5f}")

            elif tick.mid_price < alert["below"]:
                print(f"🚨 {tick.symbol_name} BELOW {alert['below']}: {tick.mid_price:.5f}")

# Usage
alerts = PriceAlerts()
handler.set_on_tick_callback(alerts.on_tick)
```

### 2. Moving Average Strategy
```python
from collections import deque

class MovingAverageStrategy:
    def __init__(self, symbol: str, period: int = 20):
        self.symbol = symbol
        self.period = period
        self.prices = deque(maxlen=period)

    def on_tick(self, tick: TickData):
        if tick.symbol_name != self.symbol:
            return

        self.prices.append(tick.mid_price)

        if len(self.prices) == self.period:
            ma = sum(self.prices) / self.period
            current_price = tick.mid_price

            if current_price > ma * 1.001:  # 0.1% above MA
                print(f"📈 BUY SIGNAL: {self.symbol} @ {current_price:.5f} (MA: {ma:.5f})")

            elif current_price < ma * 0.999:  # 0.1% below MA
                print(f"📉 SELL SIGNAL: {self.symbol} @ {current_price:.5f} (MA: {ma:.5f})")

# Usage
strategy = MovingAverageStrategy("EURUSD", 50)
handler.set_on_tick_callback(strategy.on_tick)
```

### 3. Volatility Monitor
```python
class VolatilityMonitor:
    def __init__(self):
        self.bars_history = {}

    def on_bar(self, bar: BarData):
        symbol = bar.symbol_name

        if symbol not in self.bars_history:
            self.bars_history[symbol] = deque(maxlen=20)

        self.bars_history[symbol].append(bar)

        # Calculate ATR (Average True Range)
        if len(self.bars_history[symbol]) >= 2:
            current_bar = bar
            prev_bar = list(self.bars_history[symbol])[-2]

            true_range = max(
                current_bar.high_price - current_bar.low_price,
                abs(current_bar.high_price - prev_bar.close_price),
                abs(current_bar.low_price - prev_bar.close_price)
            )

            print(f"📊 {symbol} True Range: {true_range:.5f}")

            # High volatility alert
            if true_range > 0.001:  # Adjust threshold
                print(f"⚠️  HIGH VOLATILITY: {symbol}")

# Usage
volatility = VolatilityMonitor()
handler.set_on_bar_callback(volatility.on_bar)
```

## 🔧 Subscription Management

### Subscribe to Tick Data
```python
# Subscribe to real-time price updates
handler.subscribe_to_ticks("EURUSD", subscribe_to_timestamp=True)
handler.subscribe_to_ticks("GBPUSD", subscribe_to_timestamp=True)

# Unsubscribe
handler.unsubscribe_from_ticks("EURUSD")
```

### Subscribe to Bar Data
```python
# Available periods
periods = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

# Subscribe to different timeframes
handler.subscribe_to_bars("EURUSD", "M1")    # 1-minute bars
handler.subscribe_to_bars("EURUSD", "H1")    # 1-hour bars
handler.subscribe_to_bars("GBPUSD", "M5")    # 5-minute bars
```

## ⚡ Performance Considerations

### Tick Data Frequency
- Major pairs: 100-1000+ ticks per minute during active hours
- Exotic pairs: 10-100 ticks per minute
- **Important**: Filter unnecessary processing to avoid lag

```python
def efficient_on_tick(tick: TickData):
    # Only process every 10th tick to reduce load
    if tick_counter % 10 == 0:
        perform_analysis(tick)

    # Or only process significant price moves
    if abs(tick.mid_price - last_price) > min_price_change:
        perform_analysis(tick)
```

### Bar Data Timing
- M1 bars: 1 per minute per symbol
- H1 bars: 1 per hour per symbol
- More predictable load than tick data

### Memory Management
```python
# Use deque with maxlen to limit memory usage
from collections import deque

price_history = deque(maxlen=1000)  # Keep only last 1000 prices
bar_history = deque(maxlen=100)     # Keep only last 100 bars
```

## 🛠️ Advanced Features

### Multi-Symbol Handling
```python
class MultiSymbolStrategy:
    def __init__(self):
        self.symbol_data = {}

    def on_tick(self, tick: TickData):
        symbol = tick.symbol_name

        if symbol not in self.symbol_data:
            self.symbol_data[symbol] = {
                'prices': deque(maxlen=100),
                'last_signal': None
            }

        self.symbol_data[symbol]['prices'].append(tick.mid_price)

        # Process each symbol independently
        self.analyze_symbol(symbol)
```

### Cross-Timeframe Analysis
```python
class MultiTimeframeStrategy:
    def __init__(self):
        self.m1_bars = deque(maxlen=60)   # 1-hour of M1 bars
        self.h1_bars = deque(maxlen=24)   # 1-day of H1 bars

    def on_bar(self, bar: BarData):
        if bar.period == "M1":
            self.m1_bars.append(bar)
            self.check_short_term_signals()

        elif bar.period == "H1":
            self.h1_bars.append(bar)
            self.check_long_term_trend()
```

### Real-time Statistics
```python
def log_statistics():
    stats = handler.get_statistics()
    print(f"📊 Processed {stats['tick_count']} ticks, {stats['bar_count']} bars")
    print(f"🔗 Subscribed to {stats['subscribed_symbols_ticks']} symbols (ticks)")
    print(f"📈 Subscribed to {stats['subscribed_symbols_bars']} symbols (bars)")

# Log every 30 seconds
reactor.callLater(30, log_statistics)
```

## 🚨 Important Notes

### Testing & Safety
1. **Always test with demo account first**
2. **Start with paper trading** (no real orders)
3. **Monitor performance** and memory usage
4. **Have circuit breakers** for runaway algorithms

### Connection Management
```python
def on_connection():
    print("✅ Connected - resuming strategies")
    # Re-subscribe to required symbols

def on_disconnection(reason):
    print(f"❌ Disconnected: {reason}")
    # Save state, pause trading
    # Attempt reconnection
```

### Error Handling
```python
def robust_on_tick(tick: TickData):
    try:
        # Your trading logic here
        process_tick(tick)
    except Exception as e:
        logger.error(f"Error processing tick: {e}")
        # Continue processing other ticks
```

This market data callback system gives you **real-time access** to price movements and completed bars, enabling sophisticated algorithmic trading strategies, market analysis, and automated decision making.

Remember: **Test thoroughly** before deploying any live trading algorithms! 🚨