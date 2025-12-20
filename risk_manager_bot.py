#!/usr/bin/env python
"""
Modern Risk Manager Bot using async/await instead of Twisted.
Provides comprehensive risk management with clean async interface.
"""

import asyncio
import argparse
import json
import logging
import pytz
from datetime import time, datetime, timedelta
from typing import Dict, List, Optional

from ctrader_open_api.bot import Bot
from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAReconcileReq


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def parse_hedge_time(time_str: str) -> time:
    """Parse hedge time from string format (HH:MM) to time object."""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except ValueError:
        logger.error(f"Invalid hedge time format: {time_str}. Expected HH:MM")
        raise


def validate_config(config: dict):
    """Validate that all required configuration parameters are present."""
    # Required top-level keys
    required_top_level = ['auth', 'risk_manager_config']
    for key in required_top_level:
        if key not in config:
            raise ValueError(f"Missing required configuration section: {key}")

    # Required auth parameters
    required_auth = ['client_id', 'client_secret', 'account_id', 'account_token']
    auth_config = config['auth']
    for key in required_auth:
        if key not in auth_config:
            raise ValueError(f"Missing required auth parameter: {key}")

    # Required risk manager parameters
    required_risk = [
        'allowed_symbols', 'hedge_symbols', 'freeze_minutes',
        'max_lot_volume', 'loss_threshold', 'hedge_time'
    ]
    risk_config = config['risk_manager_config']
    for key in required_risk:
        if key not in risk_config:
            raise ValueError(f"Missing required risk manager parameter: {key}")

    # Validate parameter types
    if not isinstance(risk_config['allowed_symbols'], list):
        raise ValueError("allowed_symbols must be a list")

    if not isinstance(risk_config['hedge_symbols'], list):
        raise ValueError("hedge_symbols must be a list")

    if not isinstance(risk_config['freeze_minutes'], (int, float)) or risk_config['freeze_minutes'] < 0:
        raise ValueError("freeze_minutes must be a non-negative number")

    if not isinstance(risk_config['max_lot_volume'], (int, float)) or risk_config['max_lot_volume'] <= 0:
        raise ValueError("max_lot_volume must be a positive number")

    if not isinstance(risk_config['loss_threshold'], (int, float)) or risk_config['loss_threshold'] <= 0:
        raise ValueError("loss_threshold must be a positive number")

    if not isinstance(risk_config['hedge_time'], str):
        raise ValueError("hedge_time must be a string in HH:MM format")

    # Validate hedge time format
    try:
        parse_hedge_time(risk_config['hedge_time'])
    except ValueError:
        raise ValueError("hedge_time must be in HH:MM format (e.g., '17:00')")

    logger.info("Configuration validation passed")


class RiskManagerBot(Bot):
    """
    Modern Risk Manager Bot with async/await interface.
    Provides the same risk management functionality as the original bot
    but with better error handling and no Twisted dependencies.
    """

    def __init__(self, auth: Dict, host_type: str = "demo", config: Dict = None):
        """
        Initialize the modern risk manager bot.

        Args:
            auth: Authentication credentials
            host_type: 'demo' or 'live' server
            config: Risk management configuration parameters
        """
        super().__init__(auth, host_type=host_type, auto_authenticate=True)

        # Use default config if none provided
        if config is None:
            config = {
                "allowed_symbols": ["EURUSD", "GBPUSD", "USDJPY"],
                "hedge_symbols": ["XAUUSD"],
                "freeze_minutes": 60,
                "max_lot_volume": 0.08,
                "loss_threshold": 0.01,
                "hedge_time": "17:00"
            }

        # Validate all required parameters are present
        required_params = [
            'allowed_symbols', 'hedge_symbols', 'freeze_minutes',
            'max_lot_volume', 'loss_threshold', 'hedge_time'
        ]

        for param in required_params:
            if param not in config:
                raise ValueError(f"Missing required configuration parameter: {param}")

        # Parse hedge time if it's a string
        hedge_time = config["hedge_time"]
        if isinstance(hedge_time, str):
            hedge_time = parse_hedge_time(hedge_time)

        # Risk management configuration
        self.risk_manager = RiskManager(
            trade_client=self.trade_client,
            allowed_symbols=config["allowed_symbols"],
            hedge_symbols=config["hedge_symbols"],
            freeze_minutes=config["freeze_minutes"],
            max_lot_volume=config["max_lot_volume"],
            loss_threshold=config["loss_threshold"],
            hedge_time=hedge_time,
        )


    async def on_connected(self):
        """Called when connected to cTrader server."""
        await super().on_connected()

        # Wait for authentication
        if await self.wait_for_authentication():
            logger.info("Starting risk management...")

            # Subscribe to spot prices for all symbols we care about
            all_symbols = self.risk_manager.allowed_symbols
            await self.subscribe_to_symbol_spots(all_symbols)
        else:
            logger.error("Authentication failed, risk management not started")

    async def on_disconnected(self, reason: str):
        """Called when disconnected from cTrader server."""
        logger.warning(f"Disconnected: {reason}")

        await super().on_disconnected(reason)

    async def on_tick(self, message=None):
        """
        Called on every tick - this is where risk management runs.
        """
        
        await super().on_tick(message)

        try:
            # Execute risk management logic asynchronously
            await self.risk_manager.act_async()

        except Exception as e:
            logger.error(f"Error in risk management: {e}")

    async def stop(self):
        """Stop the bot and cleanup."""
        logger.info("Stopping risk manager bot...")

        await super().stop()

    def get_cached_spot_prices(self) -> dict:
        """Get current cached spot prices for debugging."""
        return self.trade_client.spot_prices_cache

    def print_spot_prices_status(self):
        """Print current spot prices cache status."""
        cache = self.get_cached_spot_prices()
        if not cache:
            logger.info("📊 No spot prices cached yet")
        else:
            logger.info(f"📊 Cached spot prices for {len(cache)} symbols:")
            for symbol_id, price_data in cache.items():
                bid = price_data.get('bid', 'N/A')
                ask = price_data.get('ask', 'N/A')
                timestamp = price_data.get('timestamp', 'N/A')
                logger.info(f"   Symbol ID {symbol_id}: Bid={bid}, Ask={ask}, Timestamp={timestamp}")


class RiskManager:
    """
    Modern Risk Manager that works with async trade client.
    Provides comprehensive risk management with async capabilities.
    """

    def __init__(
        self,
        trade_client,
        allowed_symbols: List[str],
        hedge_symbols: List[str],
        freeze_minutes: int,
        max_lot_volume: float,
        loss_threshold: float,
        hedge_time,
    ):
        """
        Initialize with modern trade client.

        Args:
            trade_client: TradeClient instance
            allowed_symbols: List of allowed trading symbols
            hedge_symbols: List of hedge symbols
            freeze_minutes: Minutes to freeze trading after loss threshold
            max_lot_volume: Maximum lot volume per symbol
            loss_threshold: Loss threshold to trigger position closing
            hedge_time: Time to create hedge positions
            random_trade: Enable random trading for testing
        """
        self.trade_client = trade_client
        self.allowed_symbols = [s.upper() for s in allowed_symbols]
        self.hedge_symbols = [s.upper() for s in hedge_symbols]
        self.freeze_minutes = int(freeze_minutes)
        self.max_lot_volume = float(max_lot_volume)
        self.loss_threshold = float(loss_threshold)
        self.hedge_time = hedge_time

        self.freeze_start_time = None
        self.freeze_end_time = None
        self.last_hedge_execution_date = None

        # Cache for symbols data and deals
        self._symbols_data = {}
        self._deals_cache = []

    async def act_async(self):
        """
        Main risk management action method.
        Performs all risk management checks asynchronously.
        """
        # Always do these first as they don't require position data
        await self._check_freeze_period()
        await self._check_time_restrictions()

        try:
            # Get current data asynchronously
            positions = await self._get_positions_async()
            symbols_data = await self._get_symbols_async()
            deals = await self.trade_client.get_deals()

            # Store data for other methods
            self._symbols_data = symbols_data
            self._deals_cache = deals

            # Run checks that need position data
            await self._check_loss_async(positions)
            await self._check_volume_async(positions)
            await self._check_symbols_async(positions)

        except Exception as e:
            logger.error(f"Error in async risk management checks: {e}")

    # Helper Methods

    def get_server_time(self, timezone_str: str = "UTC") -> datetime:
        """Get current server time in specified timezone."""
        if timezone_str == "UTC":
            return datetime.now(pytz.UTC)
        elif timezone_str == "America/New_York":
            ny_tz = pytz.timezone("America/New_York")
            return datetime.now(ny_tz)
        else:
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)

    def get_position_entry_time(self, position) -> datetime:
        """Extract position entry time."""
        return datetime.fromtimestamp(position.tradeData.openTimestamp / 1000, tz=pytz.UTC)

    def calculate_net_lot_volume(self, symbol: str, positions_data) -> float:
        """Calculate net lot volume for a symbol (long - short)."""
        net_volume = 0.0
        symbol = symbol.upper()

        for position in positions_data:
            # Get symbol name from our symbols cache
            symbol_info = None

            for sym_name, sym_data in self._symbols_data.items():
                if sym_data.get('symbolId') == position.tradeData.symbolId:
                    symbol_info = sym_data
                    break

            if symbol_info and symbol_info.get('symbolName', '').upper() == symbol:
                # Volume is in tradeData.volume (in cents)
                volume = position.tradeData.volume / 1e7  # Convert from cents to lots

                # TradeSide: 1 = BUY, 2 = SELL
                if position.tradeData.tradeSide == 1:  # BUY
                    net_volume += volume
                else:  # SELL
                    net_volume -= volume

        return net_volume

    def _get_symbol_name_from_position(self, position) -> str:
        """Get symbol name from position using symbolId lookup."""
        if self._symbols_data:
            for sym_name, sym_data in self._symbols_data.items():
                if sym_data.get('symbolId') == position.tradeData.symbolId:
                    return sym_name
        return ""

    def _calculate_floating_pnl_with_positions(self, positions) -> float:
        """Calculate floating P&L by summing each position's unrealized P&L."""
        total_floating_pnl = 0.0

        try:
            for position in positions:
                position_pnl = self._calculate_position_floating_pnl(position)
                total_floating_pnl += position_pnl

                # Get position details for debugging
                symbol_name = self._get_symbol_name_from_position(position)
                volume_lots = position.tradeData.volume / 1e7
                trade_side = "BUY" if position.tradeData.tradeSide == 1 else "SELL"

                logger.debug(f"Position {position.positionId} ({symbol_name} {trade_side} {volume_lots:.3f}): Floating P&L ${position_pnl:.2f}")

            logger.info(f"Total floating P&L: ${total_floating_pnl:.2f}")
            return total_floating_pnl

        except Exception as e:
            logger.error(f"Error calculating floating P&L: {e}")
            return 0.0

    def _calculate_position_floating_pnl(self, position) -> float:
        """Calculate floating P&L for a single position using current market price and entry price."""
        try:
            # Get position data
            swap = position.swap / 100.0  # Convert from cents
            commission = position.commission / 100.0  # Convert from cents
            position_id = position.positionId

            # Get trade data
            trade_data = position.tradeData
            volume_lots = trade_data.volume / 1e7  # Convert from cents to lots
            trade_side = trade_data.tradeSide  # 1 = BUY, 2 = SELL
            symbol_id = trade_data.symbolId

            # Get entry price from deals
            entry_price = position.price


            # Get symbol info.
            symbol_info = None
            for sym_name, sym_data in self._symbols_data.items():
                if sym_data.get('symbolId') == symbol_id:
                    symbol_info = sym_data
                    break
            
            if not symbol_info:
                raise ValueError(f"Symbol info not found for symbol ID {symbol_id}")

            # Get current market price from trade client
            current_price = self.get_price(symbol_id, trade_side)

            # Calculate price movement P&L
            # Get pip value for proper calculation
            symbol_name = symbol_info.get('symbolName', '')
            pip_position = 1e5  # Default for most forex pairs (5 decimal places)

            # Adjust pip position based on symbol type
            if 'JPY' in symbol_name:
                pip_position = 1e3  # JPY pairs typically have 3 decimal places
            elif symbol_name in ['XAUUSD', 'XAGUSD']:  # Gold, Silver
                pip_position = 1e2  # Metals typically have 2 decimal places

            # Calculate price difference in pips
            price_diff_pips = (current_price - entry_price) * pip_position

            # Calculate P&L
            if trade_side == 1:  # BUY position
                price_pnl = price_diff_pips * volume_lots
            else:  # SELL position
                price_pnl = -price_diff_pips * volume_lots

            # For forex, assume 1 pip = $1 per standard lot (simplified)
            # In reality, you'd need to calculate pip value based on account currency

            # Total P&L = Price P&L + Swap + Commission
            total_pnl = price_pnl + swap + commission

            logger.debug(f"Position {position_id}: Entry={entry_price}, Current={current_price}, "
                        f"Volume={volume_lots:.3f}, Side={'BUY' if trade_side == 1 else 'SELL'}, "
                        f"Price P&L=${price_pnl:.2f}, Swap=${swap:.2f}, Total=${total_pnl:.2f}")

            return total_pnl

        except Exception as e:
            logger.error(f"Error calculating position P&L: {e}")
            # Fallback to swap only
            return getattr(position, 'swap', 0) / 100.0

    def _get_position_entry_price(self, position_id: int) -> float:
        """Get entry price for a position by finding the deal that created it."""
        try:
            # Find deal with matching positionId
            for deal in self._deals_cache:
                if deal.positionId == position_id:
                    execution_price = deal.executionPrice
                    logger.info(f"Found entry price for position {position_id}: {execution_price}")
                    return execution_price
                        
            # If not found in deals cache
            logger.error(f"No entry price found for position {position_id} in deals cache")
            return 0.0

        except Exception as e:
            logger.error(f"Error getting entry price for position {position_id}: {e}")
            return 0.0

    def _start_freeze_period(self):
        """Start the freeze period."""
        self.freeze_start_time = self.get_server_time()
        self.freeze_end_time = self.freeze_start_time + timedelta(minutes=self.freeze_minutes)
        logger.info(f"Freeze period started at {self.freeze_start_time}, duration: {self.freeze_minutes} minutes")

    # Data Retrieval Methods

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

    # Risk Management Checks

    async def _check_freeze_period(self):
        """Check and manage freeze period."""
        if self.freeze_start_time is None:
            return

        current_time = self.get_server_time()
        if current_time >= self.freeze_end_time:
            logger.info(f"Freeze period ended at {current_time}")
            self.freeze_start_time = None
            self.freeze_end_time = None
        else:
            # Close any new positions opened during freeze period (non-hedge)
            try:
                positions = await self._get_positions_async()
                await self._close_new_positions_during_freeze(positions)
            except Exception as e:
                logger.error(f"Error checking positions during freeze: {e}")

    async def _close_new_positions_during_freeze(self, positions):
        """Close any new positions opened during freeze period (non-hedge)."""
        if self.freeze_start_time is None:
            return

        try:
            for position in positions:
                # Get symbol name from position
                symbol_name = self._get_symbol_name_from_position(position)
                if symbol_name.upper() in self.hedge_symbols:
                    continue

                position_entry_time = self.get_position_entry_time(position)
                if self.freeze_start_time < position_entry_time <= self.freeze_end_time:
                    logger.info(f"Closing position {position.positionId} opened during freeze period at {position_entry_time}")
                    try:
                        await self.trade_client.close_position(position.positionId, position.tradeData.volume)
                    except Exception as e:
                        logger.error(f"Error closing position during freeze: {e}")
        except Exception as e:
            logger.error(f"Error processing positions for freeze check: {e}")

    async def _check_time_restrictions(self):
        """Check time-based trading restrictions - hedge logic after cutoff."""
        now_ny = self.get_server_time("America/New_York")

        if now_ny.time() >= self.hedge_time:
            current_date = now_ny.date()
            if self.last_hedge_execution_date != current_date:
                await self._handle_post_cutoff_positions()
                self.last_hedge_execution_date = current_date

    async def _handle_post_cutoff_positions(self):
        """Handle positions after NY cutoff time - create hedge positions if floating loss."""
        try:
            positions = await self._get_positions_async()
            await self._check_symbols_for_hedge(positions)
        except Exception as e:
            logger.error(f"Error checking positions for hedge: {e}")

    async def _check_symbols_for_hedge(self, positions):
        """Check each symbol for hedge requirements."""
        try:
            for symbol in self.allowed_symbols:
                floating_loss = await self._get_symbol_floating_loss_async(symbol, positions)
                if floating_loss < 0:
                    logger.info(f"Floating loss detected for {symbol} after cutoff: ${floating_loss:.2f}")
                    logger.info("Creating hedge positions instead of closing...")
                    await self._create_hedge_positions_async(symbol, positions)
        except Exception as e:
            logger.error(f"Error checking symbols for hedge: {e}")

    async def _get_symbol_floating_loss_async(self, symbol: str, positions) -> float:
        """Get floating P&L for a specific symbol."""
        floating_pnl = 0.0
        symbol = symbol.upper()

        for position in positions:
            symbol_name = self._get_symbol_name_from_position(position)
            if symbol_name.upper() == symbol:
                # For now, assume no floating loss (would need current market price)
                pass

        return floating_pnl

    async def _create_hedge_positions_async(self, symbol: str, positions):
        """Create hedge positions for the symbol."""
        net_lot_volume = self.calculate_net_lot_volume(symbol.upper(), positions)

        if abs(net_lot_volume) > 0:
            hedge_volume = abs(net_lot_volume)
            volume_in_units = int(hedge_volume * 100000)  # Convert lots to cents

            if net_lot_volume > 0:
                trade_side = 'SELL'
                logger.info(f"Creating SHORT hedge position for {symbol}: {hedge_volume:.3f} lots")
            else:
                trade_side = 'BUY'
                logger.info(f"Creating BUY hedge position for {symbol}: {hedge_volume:.3f} lots")

            # Get symbol info from cache
            symbol_info = self._symbols_data.get(symbol.upper())
            if not symbol_info:
                logger.error(f"Symbol {symbol} not found in cache")
                return

            try:
                result = await self.trade_client.execute_market_order(
                    symbol_id=symbol_info.get('symbolId'),
                    trade_side=trade_side,
                    volume=volume_in_units,
                    comment="Hedge position"
                )
                logger.info(f"Successfully created hedge position for {symbol}")
            except Exception as e:
                logger.error(f"Failed to place {trade_side} order for {symbol}: {e}")

    async def _check_loss_async(self, positions):
        """Check if current loss exceeds threshold and trigger forced closing."""
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
        """Calculate current loss with closed profit and floating P&L."""
        try:
            # Calculate floating PnL
            floating_pnl = self._calculate_floating_pnl_with_positions(positions)

            # Get closed profit asynchronously
            closed_profit_24h = await self._get_closed_profit_async(timedelta(hours=24))

            # If the closed profit is negative, treat it as zero for loss calculation
            closed_profit_24h = max(closed_profit_24h, 0.0)

            # Current loss calculation Put the negative sign
            current_loss = - (closed_profit_24h + floating_pnl)

            logger.info(f"Loss calculation: Closed profit 24h: ${closed_profit_24h:.2f}, "
                       f"Floating P&L: ${floating_pnl:.2f}, Current loss: ${current_loss:.2f}")

            return current_loss

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
        """Check and enforce position volume limits for each symbol."""
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
        """Close excess positions for a symbol to stay within volume limits."""
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
        """Check and enforce symbol restrictions."""
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
        """Close all non-hedge positions across symbols."""
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


async def main(config_path: str):
    """Main function to run the modern risk manager bot."""
    # Load configuration from JSON file
    full_config = load_config(config_path)

    # Validate configuration
    validate_config(full_config)

    # Extract auth and risk manager configuration
    auth = full_config["auth"]
    host_type = full_config.get("host_type", "demo")
    config = full_config["risk_manager_config"]

    # Create and start the bot
    bot = RiskManagerBot(auth=auth, host_type=host_type, config=config)
    await bot.start()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Risk Manager Bot")
    parser.add_argument(
        "config",
        help="Path to JSON configuration file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        asyncio.run(main(args.config))
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")