#!/usr/bin/env python
"""
Modern Risk Manager Bot using async/await instead of Twisted.
Provides comprehensive risk management with clean async interface.
"""

import asyncio
import logging
from datetime import time
from typing import Dict

from ctrader_open_api.modern_bot import ModernBot
from risk_manager import RiskManager


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModernRiskManagerBot(ModernBot):
    """
    Modern Risk Manager Bot with async/await interface.
    Provides the same risk management functionality as the original bot
    but with better error handling and no Twisted dependencies.
    """

    def __init__(self, auth: Dict, host_type: str = "demo"):
        """
        Initialize the modern risk manager bot.

        Args:
            auth: Authentication credentials
            host_type: 'demo' or 'live' server
        """
        super().__init__(auth, host_type=host_type, auto_authenticate=True)

        # Risk management configuration
        self.risk_manager = ModernRiskManager(
            trade_client=self.trade_client,
            allowed_symbols=["EURUSD", "GBPUSD", "USDJPY"],  # Configure as needed
            hedge_symbols=["XAUUSD"],  # Configure as needed
            freeze_minutes=60,
            max_lot_volume=0.08,
            loss_threshold=0.01,  # $1000 loss threshold
            hedge_time=time(17, 0),  # 5 PM NY time
            random_trade=False  # Set to True for testing
        )

        # Risk management task
        self.risk_task: asyncio.Task = None

    async def on_connected(self):
        """Called when connected to cTrader server."""
        await super().on_connected()

        # Wait for authentication
        if await self.wait_for_authentication():
            logger.info("Starting risk management...")
            # Start risk management task
            self.risk_task = asyncio.create_task(self._risk_management_loop())
        else:
            logger.error("Authentication failed, risk management not started")

    async def on_disconnected(self, reason: str):
        """Called when disconnected from cTrader server."""
        logger.warning(f"Disconnected: {reason}")

        # Stop risk management task
        if self.risk_task and not self.risk_task.done():
            self.risk_task.cancel()

        await super().on_disconnected(reason)

    async def on_tick(self, spot_event=None):
        """
        Called on every tick - this is where risk management runs.
        """
        # Only run risk management if authenticated and connected
        if not self.is_authenticated or not self.is_connected:
            return

        try:
            # Execute risk management logic asynchronously
            await self.risk_manager.act_async()

        except Exception as e:
            logger.error(f"Error in risk management: {e}")

    async def _risk_management_loop(self):
        """
        Background task for periodic risk management checks.
        Runs every few seconds to ensure risk management is active.
        """
        try:
            while self.is_running and self.is_connected:
                try:
                    if self.is_authenticated:
                        await self.risk_manager.act_async()

                except Exception as e:
                    logger.error(f"Error in risk management loop: {e}")

                # Wait before next check
                await asyncio.sleep(5)  # Check every 5 seconds

        except asyncio.CancelledError:
            logger.info("Risk management loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in risk management loop: {e}")

    async def stop(self):
        """Stop the bot and cleanup."""
        logger.info("Stopping risk manager bot...")

        # Cancel risk management task
        if self.risk_task and not self.risk_task.done():
            self.risk_task.cancel()
            try:
                await self.risk_task
            except asyncio.CancelledError:
                pass

        await super().stop()


class ModernRiskManager(RiskManager):
    """
    Modern Risk Manager that works with async trade client.
    Extends the original RiskManager with async capabilities.
    """

    def __init__(self, trade_client, **kwargs):
        """
        Initialize with modern trade client.

        Args:
            trade_client: ModernTradeClient instance
            **kwargs: Same arguments as original RiskManager
        """
        super().__init__(trade_client, **kwargs)

    async def act_async(self):
        """
        Async version of the act() method.
        Main risk management logic with async data fetching.
        """
        # Always do these first as they don't require position data
        self.check_freeze_period_async()
        self.check_time_restrictions_async()

        try:
            # Get current data asynchronously
            positions = await self._get_positions_async()
            symbols_data = await self._get_symbols_async()

            # Store symbols data for other methods
            self._symbols_data = symbols_data

            # Run checks that need position data
            await self._check_loss_async(positions)
            await self._check_volume_async(positions)
            await self._check_symbols_async(positions)

        except Exception as e:
            logger.error(f"Error in async risk management checks: {e}")

    async def _get_positions_async(self):
        """Get positions asynchronously."""
        try:
            positions = await self.trade_client.get_positions()
            logger.debug(f"Retrieved {len(positions)} positions")
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def _get_symbols_async(self):
        """Get symbols asynchronously."""
        try:
            symbols = await self.trade_client.get_symbols()
            logger.debug(f"Retrieved {len(symbols)} symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return {}

    def check_freeze_period_async(self):
        """Async version of freeze period check."""
        # This method is mostly synchronous, just renamed for consistency
        self.check_freeze_period()

    def check_time_restrictions_async(self):
        """Async version of time restrictions check."""
        # This method is mostly synchronous, just renamed for consistency
        self.check_time_restrictions()

    async def _check_loss_async(self, positions):
        """Async version of loss check."""
        try:
            current_loss = await self._get_current_loss_async(positions)

            if current_loss > self.loss_threshold:
                logger.warning(f"Loss threshold exceeded: ${current_loss:.2f} > ${self.loss_threshold}")
                logger.info("Executing forced position closing...")
                await self._close_positions_async(positions)
                self._start_freeze_period()

        except Exception as e:
            logger.error(f"Error in loss check: {e}")

    async def _get_current_loss_async(self, positions):
        """Async version of current loss calculation."""
        try:
            # Calculate floating PnL
            floating_pnl = self._calculate_floating_pnl_with_positions(positions)

            # Get closed profit asynchronously
            from datetime import timedelta
            closed_profit_24h = await self._get_closed_profit_async(timedelta(hours=24))

            # If the closed profit is negative, treat it as zero for loss calculation
            closed_profit_24h = max(closed_profit_24h, 0.0)

            # Current loss calculation
            current_loss = closed_profit_24h - floating_pnl

            logger.info(f"Loss calculation: Closed profit 24h: ${closed_profit_24h:.2f}, "
                       f"Floating P&L: ${floating_pnl:.2f}, Current loss: ${current_loss:.2f}")

            return max(current_loss, 0.0)

        except Exception as e:
            logger.error(f"Error calculating current loss: {e}")
            return 0.0

    async def _get_closed_profit_async(self, time_delta):
        """Get closed profit asynchronously."""
        try:
            return await self.trade_client.calculate_closed_profit(time_delta)
        except Exception as e:
            logger.error(f"Error getting closed profit: {e}")
            return 0.0

    async def _check_volume_async(self, positions):
        """Async version of volume check."""
        try:
            for symbol in self.allowed_symbols:
                if not symbol:
                    continue

                net_volume = abs(self.calculate_net_lot_volume(symbol, positions))

                if net_volume > self.max_lot_volume:
                    logger.warning(f"Excess net volume detected for {symbol}: "
                                 f"{net_volume:.3f} > {self.max_lot_volume:.3f} lots")
                    await self._close_excess_positions_async(symbol, net_volume - self.max_lot_volume, positions)

        except Exception as e:
            logger.error(f"Error in volume check: {e}")

    async def _close_excess_positions_async(self, symbol, excess_volume, positions):
        """Async version of closing excess positions."""
        try:
            symbol = symbol.upper()
            symbol_positions = [
                pos for pos in positions
                if self._get_symbol_name_from_position(pos).upper() == symbol
            ]
            symbol_positions.sort(key=lambda x: x.tradeData.openTimestamp, reverse=True)

            for position in symbol_positions:
                current_net_volume = abs(self.calculate_net_lot_volume(symbol, positions))
                if current_net_volume <= self.max_lot_volume:
                    logger.info(f"Net volume now within limit for {symbol}: "
                              f"{current_net_volume:.3f} <= {self.max_lot_volume:.3f}")
                    break

                position_volume_lots = position.tradeData.volume / 1e7
                position_id = position.positionId
                trade_type = "BUY" if position.tradeData.tradeSide == 1 else "SELL"

                logger.info(f"Closing position {position_id} ({trade_type}) "
                           f"with volume {position_volume_lots:.3f} lots")

                try:
                    await self.trade_client.close_position(position_id, position.tradeData.volume)
                except Exception as e:
                    logger.error(f"Error closing excess position: {e}")

        except Exception as e:
            logger.error(f"Error closing excess positions: {e}")

    async def _check_symbols_async(self, positions):
        """Async version of symbol restrictions check."""
        try:
            allowed_and_hedge = self.allowed_symbols + self.hedge_symbols

            for position in positions:
                symbol_name = self._get_symbol_name_from_position(position).upper()
                if symbol_name not in allowed_and_hedge:
                    position_id = position.positionId
                    volume = position.tradeData.volume
                    logger.warning(f"Forbidden symbol detected: {symbol_name}")
                    logger.info(f"Closing position {position_id} for forbidden symbol")

                    try:
                        await self.trade_client.close_position(position_id, volume)
                    except Exception as e:
                        logger.error(f"Error closing forbidden symbol position: {e}")

        except Exception as e:
            logger.error(f"Error in symbol check: {e}")

    async def _close_positions_async(self, positions):
        """Async version of closing positions."""
        try:
            positions_closed = 0
            for position in positions:
                symbol_name = self._get_symbol_name_from_position(position).upper()
                if symbol_name not in self.hedge_symbols:
                    position_id = position.positionId
                    logger.info(f"Closing position on {symbol_name} id {position_id}...")

                    try:
                        await self.trade_client.close_position(position_id, position.tradeData.volume)
                        logger.info(f"Position {position_id} closed.")
                        positions_closed += 1
                    except Exception as e:
                        logger.error(f"Error closing position {position_id}: {e}")

            if positions_closed == 0:
                logger.info("No positions found to close (non-hedge)")
            else:
                logger.info(f"Closed {positions_closed} positions (non-hedge)")

        except Exception as e:
            logger.error(f"Error closing positions: {e}")


async def main():
    """Main function to run the modern risk manager bot."""
    auth = {
        "client_id": "7870_AGNoUDByyfLOPTiKMGwZHQbK5whzvUNo2BpTCsTXff3ajFz8my",
        "client_secret": "0xtJwsbjTul1lmjjOI5rwSaViVIhcMJNqW8bWNzARwHVwQdeuA",
        "account_id": 45416297,
        "account_token": "-KwZawTvJbMvSGaPaQ-Rrt96CltxaiCsWAEK_6IuSDE",
    }

    bot = ModernRiskManagerBot(auth=auth)
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")