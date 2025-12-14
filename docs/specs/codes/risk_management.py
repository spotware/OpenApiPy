import clr
from datetime import datetime, timedelta
from datetime_utils import get_server_time, parse_time_string
from logger_utils import get_logger
from position_utils import (
    get_position_entry_time,
    calculate_net_lot_volume,
    get_closed_profit,
)


clr.AddReference("cAlgo.API")

# Import cAlgo API types
from cAlgo.API import *


logger = get_logger()


class RiskManager:
    def __init__(
        self,
        allowed_symbols,
        hedge_symbols,
        freeze_minutes,
        max_lot_volume,
        loss_threshold,
        hedge_time,
        random_trade: bool,
    ):
        self.allowed_symbols = [s.upper() for s in allowed_symbols]  # Make sure it is always uppercase.
        self.hedge_symbols = [s.upper() for s in hedge_symbols]
        self.freeze_minutes = int(freeze_minutes)
        self.max_lot_volume = float(max_lot_volume)
        self.loss_threshold = float(loss_threshold)
        self.hedge_time = hedge_time
        self.random_trade_enabled = bool(random_trade)

        self.freeze_start_time = None
        self.freeze_end_time = None
        self.last_hedge_execution_date = None
        logger = get_logger("RiskManager")

    def act(self):
        self.random_trade()
        self.check_freeze_period()
        self.check_loss()
        self.check_volume()
        self.check_symbols()
        self.check_time_restrictions()

    def random_trade(self):
        """Optional random trade for testing."""
        if not self.random_trade_enabled:
            return

        if not self.allowed_symbols:
            return
        
        server_time = get_server_time()

        symbol_name = self.allowed_symbols[0]
        symbol = api.Symbols.GetSymbol(symbol_name)
        
        # Always trade at 09:01 (UTC) server time for testing
        if server_time.time().hour == 9 and server_time.time().minute == 1:
            volume_in_units = symbol.VolumeInUnitsMin * 1
            logger.info(f"Placing random BUY order for {symbol_name} at {server_time}")
            result = api.ExecuteMarketOrder(TradeType.Buy, symbol_name, volume_in_units)
            if result.IsSuccessful:
                logger.info(f"Random BUY order placed successfully for {symbol_name}")
            else:
                logger.warning(f"Failed to place random BUY order for {symbol_name}: {result.Error}")

    def check_freeze_period(self):
        """Check and manage freeze period"""
        if self.freeze_start_time is None:
            return

        current_time = get_server_time()
        if current_time >= self.freeze_end_time:
            logger.info(f"Freeze period ended at {current_time}")
            self.freeze_start_time = None
            self.freeze_end_time = None
        else:
            self._close_new_positions_during_freeze()

    def _close_new_positions_during_freeze(self):
        """Close any new positions opened during freeze period (non-hedge)."""
        if self.freeze_start_time is None:
            return

        for position in api.Positions:
            if position.SymbolName.upper() in self.hedge_symbols:
                continue

            position_entry_time = get_position_entry_time(position)
            if self.freeze_start_time < position_entry_time <= self.freeze_end_time:
                logger.info(
                    f"Closing position {position.Id} opened during freeze period at {position.EntryTime}"
                )
                api.ClosePosition(position)

    def check_symbols(self):
        """Check and enforce symbol restrictions"""
        for position in api.Positions:
            if position.SymbolName.upper() not in (self.allowed_symbols + self.hedge_symbols):
                logger.warning(f"Forbidden symbol detected: {position.SymbolName}")
                logger.info(f"Closing position {position.Id} for forbidden symbol")
                api.ClosePosition(position)

    def check_volume(self):
        """Check and enforce position volume limits. Each symbol separately."""
        for symbol in self.allowed_symbols:
            if not symbol:
                continue
            net_volume = abs(calculate_net_lot_volume(symbol))

            if net_volume > self.max_lot_volume:
                logger.info(
                    f"Excess net volume detected for {symbol}: {net_volume:.3f} > {self.max_lot_volume:.3f} lots"
                )
                self._close_excess_positions(symbol, net_volume - self.max_lot_volume)

    def _close_excess_positions(self, symbol, excess_volume):
        symbol = symbol.upper()
        symbol_positions = [
            pos for pos in api.Positions if pos.SymbolName.upper() == symbol
        ]
        symbol_positions.sort(key=lambda x: x.EntryTime, reverse=True)

        logger.info(
            f"Starting to close excess positions for {symbol}. Target reduction: {excess_volume:.3f} lots"
        )

        for position in symbol_positions:
            current_net_volume = abs(calculate_net_lot_volume(symbol))
            if current_net_volume <= self.max_lot_volume:
                logger.info(
                    f"Net volume now within limit for {symbol}: {current_net_volume:.3f} <= {self.max_lot_volume:.3f}"
                )
                break

            position_lot_volume = api.Symbols.GetSymbol(symbol).VolumeInUnitsToQuantity(position.VolumeInUnits)
            logger.info(
                f"Closing position {position.Id} ({position.TradeType}) with volume {position_lot_volume:.3f} lots"
            )
            api.ClosePosition(position)

        final_net_volume = abs(calculate_net_lot_volume(symbol))
        if final_net_volume <= self.max_lot_volume:
            logger.info(
                f"Successfully reduced {symbol} net volume to {final_net_volume:.3f} lots"
            )
        else:
            logger.warning(
                f"Warning: {symbol} net volume still exceeds limit: {final_net_volume:.3f} > {self.max_lot_volume:.3f}"
            )

    def check_loss(self):
        """Check if current loss exceeds threshold and trigger forced closing"""
        current_loss = self._get_current_loss()

        if current_loss > self.loss_threshold:
            logger.warning(
                f"Loss threshold exceeded: ${current_loss:.2f} > ${self.loss_threshold}"
            )
            logger.info("Executing forced position closing...")
            self._close_positions()
            self._start_freeze_period()

    def _get_current_loss(self) -> float:
        """Calculate: 24h closed profit minus floating_loss. If there is loss, the returnred value is positive."""
        # Compute floating PnL across all open positions
        floating_pnl = 0.0
        for position in api.Positions:
            try:
                floating_pnl += float(position.NetProfit)
            except Exception:
                floating_pnl += position.NetProfit

        # Get closed profit in last 24 hours
        closed_profit_24h = get_closed_profit(timedelta(hours=24))

        # If the closed profit is negative, treat it as zero for loss calculation.
        closed_profit_24h = max(closed_profit_24h, 0.0)

        # Current loss as requested: total closed profit in last 24h minus floating_loss
        current_loss = - floating_pnl - closed_profit_24h
        return current_loss

    def _close_positions(self):
        """Close all non-hedge positions across symbols"""
        positions_closed = 0
        for position in api.Positions:
            if position.SymbolName.upper() not in self.hedge_symbols:
                logger.info(
                    f"Closing position on {position.SymbolName} id {position.Id}..."
                )
                api.ClosePosition(position)
                logger.info(f"Position {position.Id} closed.")
                positions_closed += 1

        if positions_closed == 0:
            logger.info("No positions found to close (non-hedge)")
        else:
            logger.info(f"Closed {positions_closed} positions (non-hedge)")

    def _start_freeze_period(self):
        """Start the freeze period"""
        self.freeze_start_time = get_server_time()
        self.freeze_end_time = self.freeze_start_time + timedelta(
            minutes=self.freeze_minutes
        )
        logger.info(
            f"Freeze period started at {self.freeze_start_time}, duration: {self.freeze_minutes} minutes"
        )

    def check_time_restrictions(self):
        """Check time-based trading restrictions - hedge logic after cutoff"""
        now_ny = get_server_time("America/New_York")

        if now_ny.time() >= self.hedge_time:
            current_date = now_ny.date()
            if self.last_hedge_execution_date != current_date:
                self._handle_post_cutoff_positions()
                self.last_hedge_execution_date = current_date

    def _handle_post_cutoff_positions(self):
        """Handle positions after NY cutoff time - create hedge positions if floating loss"""
        for symbol in self.allowed_symbols:
            floating_loss = self._get_symbol_floating_loss(symbol)
            if floating_loss < 0:
                logger.info(
                    f"Floating loss detected for {symbol} after cutoff: ${floating_loss:.2f}"
                )
                logger.info("Creating hedge positions instead of closing...")
                self._create_hedge_positions(symbol)

    def _get_symbol_floating_loss(self, symbol):
        """Get floating P&L for a specific symbol"""
        floating_pnl = 0.0
        for position in api.Positions:
            if position.SymbolName.upper() == symbol.upper():
                floating_pnl += position.NetProfit
        return floating_pnl

    def _create_hedge_positions(self, symbol):
        """Create hedge positions for the symbol"""
        net_lot_volume = calculate_net_lot_volume(symbol.upper())

        if abs(net_lot_volume) > 0:
            hedge_volume = abs(net_lot_volume)
            volume_in_units = api.Symbols.GetSymbol(symbol).QuantityToVolumeInUnits(hedge_volume)
            if net_lot_volume > 0:
                trade_type = TradeType.Sell
                logger.info(
                    f"Creating SHORT hedge position for {symbol}: {hedge_volume:.3f} lots. Volume in units: {volume_in_units}"
                )
            else:
                trade_type = TradeType.Buy
                logger.info(
                    f"Creating BUY hedge position for {symbol}: {hedge_volume:.3f} lots. Volume in units: {volume_in_units}"
                )

            logger.info(
                f"Creating {trade_type} hedge position for {symbol}: {hedge_volume:.3f} lots. Volume in units: {volume_in_units}"
            )
            result = api.ExecuteMarketOrder(trade_type, symbol, volume_in_units)
            if result.IsSuccessful:
                logger.info(
                    f"Successfully hedge position created for {symbol} to neutralize risk"
                )
            else:
                logger.warning(f"Failed to place {trade_type} order for {symbol}: {result.Error}")

