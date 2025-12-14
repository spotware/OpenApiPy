#!/usr/bin/env python3
"""
Trading Strategy Example using Market Data Callbacks
Demonstrates how to use on_tick and on_bar callbacks for algorithmic trading

This example implements a simple moving average crossover strategy:
- Subscribes to real-time tick and bar data
- Calculates moving averages
- Generates buy/sell signals on crossovers
- Places market orders automatically

IMPORTANT: This is for educational purposes - test thoroughly before live trading!
"""

import datetime
import logging
from collections import deque
from dataclasses import dataclass
from typing import List, Optional

from market_data_handler import MarketDataHandler, TickData, BarData
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Trading signal"""
    symbol: str
    action: str  # "BUY" or "SELL"
    price: float
    timestamp: datetime.datetime
    reason: str


class MovingAverageCrossoverStrategy:
    """Simple moving average crossover strategy"""

    def __init__(self, market_handler: MarketDataHandler, symbol: str, fast_period: int = 10, slow_period: int = 20):
        self.market_handler = market_handler
        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period

        # Price history for moving averages
        self.prices = deque(maxlen=max(fast_period, slow_period) + 1)

        # Current position tracking
        self.current_position = None  # None, "LONG", or "SHORT"
        self.entry_price = None
        self.entry_time = None

        # Statistics
        self.signals_generated = 0
        self.trades_executed = 0
        self.last_signal_time = None

        logger.info(f"📈 Strategy initialized for {symbol}")
        logger.info(f"   Fast MA: {fast_period} periods")
        logger.info(f"   Slow MA: {slow_period} periods")

    def add_price(self, price: float, timestamp: datetime.datetime):
        """Add new price to history and check for signals"""
        self.prices.append((price, timestamp))

        # Need enough data for both moving averages
        if len(self.prices) >= self.slow_period:
            self.check_for_signal(price, timestamp)

    def calculate_moving_average(self, period: int) -> Optional[float]:
        """Calculate simple moving average"""
        if len(self.prices) < period:
            return None

        recent_prices = list(self.prices)[-period:]
        return sum(price for price, _ in recent_prices) / period

    def check_for_signal(self, current_price: float, timestamp: datetime.datetime):
        """Check for moving average crossover signals"""
        fast_ma = self.calculate_moving_average(self.fast_period)
        slow_ma = self.calculate_moving_average(self.slow_period)

        if fast_ma is None or slow_ma is None:
            return

        # Get previous MAs to detect crossover
        if len(self.prices) < self.slow_period + 1:
            return

        # Calculate previous MAs
        prev_prices = deque(list(self.prices)[:-1])
        prev_fast = sum(price for price, _ in list(prev_prices)[-self.fast_period:]) / self.fast_period
        prev_slow = sum(price for price, _ in list(prev_prices)[-self.slow_period:]) / self.slow_period

        signal = None

        # Detect bullish crossover (fast MA crosses above slow MA)
        if prev_fast <= prev_slow and fast_ma > slow_ma and self.current_position != "LONG":
            signal = Signal(
                symbol=self.symbol,
                action="BUY",
                price=current_price,
                timestamp=timestamp,
                reason=f"MA crossover: Fast({fast_ma:.5f}) > Slow({slow_ma:.5f})"
            )

        # Detect bearish crossover (fast MA crosses below slow MA)
        elif prev_fast >= prev_slow and fast_ma < slow_ma and self.current_position != "SHORT":
            signal = Signal(
                symbol=self.symbol,
                action="SELL",
                price=current_price,
                timestamp=timestamp,
                reason=f"MA crossover: Fast({fast_ma:.5f}) < Slow({slow_ma:.5f})"
            )

        if signal:
            self.process_signal(signal)

    def process_signal(self, signal: Signal):
        """Process trading signal"""
        self.signals_generated += 1
        self.last_signal_time = signal.timestamp

        logger.info(f"🚨 SIGNAL #{self.signals_generated}: {signal.action} {signal.symbol} at {signal.price:.5f}")
        logger.info(f"   Reason: {signal.reason}")
        logger.info(f"   Time: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # In a real implementation, you would place orders here
        # self.place_order(signal)

        # Update position tracking
        if signal.action == "BUY":
            if self.current_position == "SHORT":
                logger.info("📤 Closing SHORT position and opening LONG")
            else:
                logger.info("📈 Opening LONG position")
            self.current_position = "LONG"

        elif signal.action == "SELL":
            if self.current_position == "LONG":
                logger.info("📤 Closing LONG position and opening SHORT")
            else:
                logger.info("📉 Opening SHORT position")
            self.current_position = "SHORT"

        self.entry_price = signal.price
        self.entry_time = signal.timestamp

    def place_order(self, signal: Signal):
        """Place actual market order (implement this for live trading)"""
        logger.warning("⚠️  Order placement not implemented - this is a demo!")

        # Example implementation (uncomment and modify for live trading):
        """
        try:
            request = ProtoOANewOrderReq()
            request.ctidTraderAccountId = self.market_handler.account_id
            request.symbolId = self.market_handler.symbols[signal.symbol]
            request.orderType = ProtoOAOrderType.MARKET
            request.tradeSide = ProtoOATradeSide.BUY if signal.action == "BUY" else ProtoOATradeSide.SELL
            request.volume = 10000  # 0.1 lots
            request.comment = f"MA Strategy: {signal.reason}"

            deferred = self.market_handler.client.send(request)
            deferred.addCallbacks(
                lambda result: logger.info(f"✅ Order placed successfully"),
                lambda failure: logger.error(f"❌ Order failed: {failure}")
            )

            self.trades_executed += 1

        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
        """

    def get_statistics(self):
        """Get strategy statistics"""
        return {
            'symbol': self.symbol,
            'signals_generated': self.signals_generated,
            'trades_executed': self.trades_executed,
            'current_position': self.current_position,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time,
            'last_signal_time': self.last_signal_time,
            'data_points': len(self.prices),
            'fast_ma': self.calculate_moving_average(self.fast_period),
            'slow_ma': self.calculate_moving_average(self.slow_period)
        }


class TradingBot:
    """Main trading bot that combines market data with strategy"""

    def __init__(self):
        self.market_handler = MarketDataHandler()
        self.strategies = {}
        self.last_tick_time = {}
        self.tick_count = 0

        # Set up callbacks
        self.market_handler.set_on_tick_callback(self.on_tick)
        self.market_handler.set_on_bar_callback(self.on_bar)
        self.market_handler.set_on_connection_callback(self.on_connection)
        self.market_handler.set_on_disconnection_callback(self.on_disconnection)

    def add_strategy(self, strategy: MovingAverageCrossoverStrategy):
        """Add a trading strategy"""
        self.strategies[strategy.symbol] = strategy
        logger.info(f"📊 Added strategy for {strategy.symbol}")

    def on_tick(self, tick: TickData):
        """Handle incoming tick data"""
        self.tick_count += 1
        self.last_tick_time[tick.symbol_name] = tick.timestamp

        # Use mid price for strategy calculations
        mid_price = tick.mid_price

        # Feed price to relevant strategy
        if tick.symbol_name in self.strategies:
            self.strategies[tick.symbol_name].add_price(mid_price, tick.timestamp)

        # Log every 50 ticks to avoid spam
        if self.tick_count % 50 == 0:
            logger.info(f"📊 Processed {self.tick_count} ticks. Latest: {tick.symbol_name} @ {mid_price:.5f}")

    def on_bar(self, bar: BarData):
        """Handle incoming bar data"""
        logger.info(f"📈 BAR: {bar.symbol_name} {bar.period} - Close: {bar.close_price:.5f} Volume: {bar.volume}")

        # You could also use bar closing prices for strategy signals
        if bar.symbol_name in self.strategies:
            self.strategies[bar.symbol_name].add_price(bar.close_price, bar.timestamp)

    def on_connection(self):
        """Handle connection events"""
        logger.info("🟢 Trading bot connected to market data!")

    def on_disconnection(self, reason: str):
        """Handle disconnection events"""
        logger.warning(f"🔴 Trading bot disconnected: {reason}")

    def start_trading(self, symbols_and_strategies: List[tuple]):
        """
        Start trading with specified symbols and strategies

        Args:
            symbols_and_strategies: List of (symbol, fast_period, slow_period) tuples
        """
        logger.info("🚀 Starting trading bot...")

        # Start market data handler
        self.market_handler.start()

        # Wait for authentication then set up strategies
        def setup_strategies():
            if self.market_handler.is_authenticated:
                logger.info("🔧 Setting up trading strategies...")

                for symbol, fast_period, slow_period in symbols_and_strategies:
                    # Create and add strategy
                    strategy = MovingAverageCrossoverStrategy(
                        self.market_handler, symbol, fast_period, slow_period
                    )
                    self.add_strategy(strategy)

                    # Subscribe to market data
                    self.market_handler.subscribe_to_ticks(symbol, True)
                    self.market_handler.subscribe_to_bars(symbol, "M1")

                logger.info("✅ All strategies set up and subscriptions active!")

            else:
                # Check again in 1 second
                reactor.callLater(1, setup_strategies)

        # Start setup after 3 seconds
        reactor.callLater(3, setup_strategies)

        # Log statistics every 60 seconds
        def log_stats():
            logger.info("📊 TRADING STATISTICS:")
            for symbol, strategy in self.strategies.items():
                stats = strategy.get_statistics()
                logger.info(f"   {symbol}:")
                logger.info(f"     Signals: {stats['signals_generated']}")
                logger.info(f"     Position: {stats['current_position'] or 'NONE'}")
                logger.info(f"     Fast MA: {stats['fast_ma']:.5f}" if stats['fast_ma'] else "     Fast MA: Not enough data")
                logger.info(f"     Slow MA: {stats['slow_ma']:.5f}" if stats['slow_ma'] else "     Slow MA: Not enough data")

            reactor.callLater(60, log_stats)

        reactor.callLater(15, log_stats)

    def stop(self):
        """Stop the trading bot"""
        logger.info("⏹️  Stopping trading bot...")
        self.market_handler.stop()


def main():
    """Main function - example usage"""
    logger.info("🤖 Starting Algorithmic Trading Bot")
    logger.info("=" * 50)

    # Configuration
    STRATEGIES = [
        ("EURUSD", 5, 15),    # Fast: 5-tick MA, Slow: 15-tick MA
        ("GBPUSD", 10, 20),   # Fast: 10-tick MA, Slow: 20-tick MA
    ]

    logger.info("📋 Strategy Configuration:")
    for symbol, fast, slow in STRATEGIES:
        logger.info(f"   {symbol}: MA({fast}) vs MA({slow})")
    logger.info("=" * 50)

    logger.warning("⚠️  THIS IS A DEMO - NO ACTUAL ORDERS WILL BE PLACED")
    logger.warning("⚠️  MODIFY place_order() METHOD FOR LIVE TRADING")
    logger.info("=" * 50)

    try:
        # Create and start trading bot
        bot = TradingBot()
        bot.start_trading(STRATEGIES)

        # Run reactor
        logger.info("🎯 Trading bot started! Press Ctrl+C to stop.")
        reactor.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down trading bot...")
        if 'bot' in locals():
            bot.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()