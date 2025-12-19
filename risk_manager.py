from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from ctrader_open_api.trade_client import TradeClient


class RiskManager:
    def __init__(
        self,
        trade_client: TradeClient,
        allowed_symbols: List[str],
        hedge_symbols: List[str],
        freeze_minutes: int,
        max_lot_volume: float,
        loss_threshold: float,
        hedge_time,
        random_trade: bool = False,
    ):
        self.trade_client: TradeClient = trade_client
        self.allowed_symbols = [s.upper() for s in allowed_symbols]
        self.hedge_symbols = [s.upper() for s in hedge_symbols]
        self.freeze_minutes = int(freeze_minutes)
        self.max_lot_volume = float(max_lot_volume)
        self.loss_threshold = float(loss_threshold)
        self.hedge_time = hedge_time
        self.random_trade_enabled = bool(random_trade)

        self.freeze_start_time = None
        self.freeze_end_time = None
        self.last_hedge_execution_date = None

    def act(self):
        """Main action method - call all risk management checks"""
        # Always do these first as they don't require position data
        # self.random_trade()
        self.check_freeze_period()
        self.check_time_restrictions()

        # Get current positions and symbols synchronously
        try:
            positions = self.trade_client.get_positions_sync()
            self._symbols_data = self.trade_client.get_symbols_sync()

            # Now run checks that need position data
            self.check_loss_with_positions(positions)
            self.check_volume_with_positions(positions)
            self.check_symbols_with_positions(positions)

        except Exception as e:
            print(f"Error in risk management checks: {e}")

    def get_server_time(self, timezone_str: str = "UTC") -> datetime:
        """Replace get_server_time with current time"""
        if timezone_str == "UTC":
            return datetime.now(pytz.UTC)
        elif timezone_str == "America/New_York":
            ny_tz = pytz.timezone("America/New_York")
            return datetime.now(ny_tz)
        else:
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)

    def get_position_entry_time(self, position) -> datetime:
        """Extract position entry time"""
        # Position entry time is in tradeData.openTimestamp
        if hasattr(position, 'tradeData') and hasattr(position.tradeData, 'openTimestamp'):
            return datetime.fromtimestamp(position.tradeData.openTimestamp / 1000, tz=pytz.UTC)
        else:
            # Fallback to current time if no entry time available
            return self.get_server_time()

    def calculate_net_lot_volume(self, symbol: str, positions_data) -> float:
        """Calculate net lot volume for a symbol (long - short)"""
        net_volume = 0.0
        symbol = symbol.upper()

        for position in positions_data:
            if hasattr(position, 'tradeData') and hasattr(position.tradeData, 'symbolId'):
                # Get symbol name from our symbols cache
                symbols_data = getattr(self, '_symbols_data', {})
                symbol_info = None

                for sym_name, sym_data in symbols_data.items():
                    if sym_data.get('symbolId') == position.tradeData.symbolId:
                        symbol_info = sym_data
                        break

                if symbol_info and symbol_info.get('symbolName', '').upper() == symbol:
                    # Volume is in tradeData.volume (in cents)
                    # print("position volume:", position.tradeData.volume)
                    volume = position.tradeData.volume / 1e7  # Convert from cents to lots

                    # TradeSide: 1 = BUY, 2 = SELL
                    if position.tradeData.tradeSide == 1:  # BUY
                        net_volume += volume
                    else:  # SELL
                        net_volume -= volume

        return net_volume

    def _get_symbol_name_from_position(self, position) -> str:
        """Get symbol name from position using symbolId lookup"""
        if hasattr(position, 'tradeData') and hasattr(position.tradeData, 'symbolId'):
            symbols_data = getattr(self, '_symbols_data', {})
            if symbols_data:  # New structure from TradeClient
                for sym_name, sym_data in symbols_data.items():
                    if sym_data.get('symbolId') == position.tradeData.symbolId:
                        return sym_name
        return ""

    def get_closed_profit(self, time_delta: timedelta) -> float:
        """Get closed profit for the specified time period"""
        try:
            return self.trade_client.get_closed_profit_sync(time_delta)
        except Exception as e:
            print(f"Error getting closed profit: {e}")
            return 0.0

    # def random_trade(self):
    #     """Optional random trade for testing."""
    #     if not self.random_trade_enabled:
    #         return

    #     if not self.allowed_symbols:
    #         return

    #     server_time = self.get_server_time()

    #     symbol_name = self.allowed_symbols[0]

    #     # Always trade at 09:01 (UTC) server time for testing
    #     if server_time.time().hour == 9 and server_time.time().minute == 1:
    #         # Get symbol info from cache
    #         symbol_info = getattr(self, '_symbols_data', {}).get(symbol_name)
    #         if not symbol_info:
    #             print(f"Symbol {symbol_name} not found in cache")
    #             return

    #         volume_in_units = 100000  # 0.01 lots equivalent
    #         print(f"Placing random BUY order for {symbol_name} at {server_time}")

    #         try:
    #             # Use TradeClient to place order
    #             result = self.trade_client.execute_market_order(
    #                 symbol_id=symbol_info.get('symbolId'),
    #                 trade_side='BUY',
    #                 volume=volume_in_units,
    #                 comment="Random trade"
    #             )
    #             print(f"Random BUY order placed successfully for {symbol_name}")
    #         except Exception as e:
    #             print(f"Failed to place random BUY order for {symbol_name}: {e}")

    def check_freeze_period(self):
        """Check and manage freeze period"""
        if self.freeze_start_time is None:
            return

        current_time = self.get_server_time()
        if current_time >= self.freeze_end_time:
            print(f"Freeze period ended at {current_time}")
            self.freeze_start_time = None
            self.freeze_end_time = None
        else:
            # Close any new positions opened during freeze period (non-hedge)
            try:
                positions = self.trade_client.get_positions_sync()
                self._close_new_positions_during_freeze(positions)
            except Exception as e:
                print(f"Error checking positions during freeze: {e}")

    def _close_new_positions_during_freeze(self, positions):
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
                    print(f"Closing position {position.positionId} opened during freeze period at {position_entry_time}")
                    try:
                        self.trade_client.close_position(position.positionId, position.tradeData.volume)
                    except Exception as e:
                        print(f"Error closing position during freeze: {e}")
        except Exception as e:
            print(f"Error processing positions for freeze check: {e}")

    def check_symbols_with_positions(self, positions):
        """Check and enforce symbol restrictions"""
        allowed_and_hedge = self.allowed_symbols + self.hedge_symbols

        for position in positions:
            symbol_name = self._get_symbol_name_from_position(position).upper()
            if symbol_name not in allowed_and_hedge:
                position_id = position.positionId
                volume = position.tradeData.volume
                print(f"Forbidden symbol detected: {symbol_name}")
                print(f"Closing position {position_id} for forbidden symbol")
                try:
                    self.trade_client.close_position(position_id, volume)
                except Exception as e:
                    print(f"Error closing forbidden symbol position: {e}")

    def check_volume_with_positions(self, positions):
        """Check and enforce position volume limits. Each symbol separately."""
        for symbol in self.allowed_symbols:
            if not symbol:
                continue
            net_volume = abs(self.calculate_net_lot_volume(symbol, positions))

            if net_volume > self.max_lot_volume:
                print(f"Excess net volume detected for {symbol}: {net_volume:.3f} > {self.max_lot_volume:.3f} lots")
                self._close_excess_positions_with_positions(symbol, net_volume - self.max_lot_volume, positions)

    def _close_excess_positions_with_positions(self, symbol: str, excess_volume: float, positions):
        symbol = symbol.upper()
        symbol_positions = [
            pos for pos in positions
            if self._get_symbol_name_from_position(pos).upper() == symbol
        ]
        symbol_positions.sort(key=lambda x: x.tradeData.openTimestamp, reverse=True)

        # print(f"Starting to close excess positions for {symbol}. Target reduction: {excess_volume:.3f} lots")

        for position in symbol_positions:
            current_net_volume = abs(self.calculate_net_lot_volume(symbol, positions))
            if current_net_volume <= self.max_lot_volume:
                print(f"Net volume now within limit for {symbol}: {current_net_volume:.3f} <= {self.max_lot_volume:.3f}")
                break

            position_volume_lots = position.tradeData.volume / 1e7  # Convert to lots
            position_id = position.positionId
            trade_type = "BUY" if position.tradeData.tradeSide == 1 else "SELL"

            print(f"Closing position {position_id} ({trade_type}) with volume {position_volume_lots:.3f} lots")
            try:
                self.trade_client.close_position(position_id, position.tradeData.volume)
            except Exception as e:
                print(f"Error closing excess position: {e}")

    def check_loss_with_positions(self, positions):
        """Check if current loss exceeds threshold and trigger forced closing"""
        current_loss = self._get_current_loss_with_positions(positions)

        if current_loss > self.loss_threshold:
            print(f"Loss threshold exceeded: ${current_loss:.2f} > ${self.loss_threshold}")
            print("Executing forced position closing...")
            self._close_positions_with_data(positions)
            self._start_freeze_period()

    def _get_current_loss_with_positions(self, positions) -> float:
        """Calculate: 24h closed profit minus floating_loss. If there is loss, the returned value is positive."""
        try:
            # Calculate floating PnL by summing each position's unrealized P&L
            floating_pnl = self._calculate_floating_pnl_with_positions(positions)

            # Get closed profit in last 24 hours
            closed_profit_24h = self.get_closed_profit(timedelta(hours=24))

            # If the closed profit is negative, treat it as zero for loss calculation.
            closed_profit_24h = max(closed_profit_24h, 0.0)

            # Current loss as requested: closed profit minus floating loss
            # If floating_pnl is negative (loss), then -floating_pnl becomes positive (loss amount)
            current_loss = closed_profit_24h - floating_pnl

            print(f"Loss calculation: Closed profit 24h: ${closed_profit_24h:.2f}, Floating P&L: ${floating_pnl:.2f}, Current loss: ${current_loss:.2f}")

            # If deal history is unavailable and we have significant floating loss,
            # use conservative approach - treat floating loss as the primary indicator
            if not hasattr(self, '_last_closed_profit_time') and floating_pnl < -50.0:
                print(f"Warning: Using floating P&L as loss indicator due to unavailable deal history")
                return abs(floating_pnl)

            # Return the loss amount (positive value indicates loss)
            return max(current_loss, 0.0)

        except Exception as e:
            print(f"Error calculating current loss: {e}")
            # Fallback: if we can't calculate properly, use floating loss as indicator
            try:
                floating_pnl = self._calculate_floating_pnl_with_positions(positions)
                if floating_pnl < 0:
                    print(f"Using floating P&L fallback: ${abs(floating_pnl):.2f}")
                    return abs(floating_pnl)
            except:
                pass
            return 0.0

    def _calculate_floating_pnl_with_positions(self, positions) -> float:
        """Calculate floating P&L by summing each position's unrealized P&L"""
        total_floating_pnl = 0.0

        try:
            for position in positions:
                position_pnl = self._calculate_position_floating_pnl(position)
                total_floating_pnl += position_pnl

                # Get position details for debugging
                symbol_name = self._get_symbol_name_from_position(position)
                volume_lots = position.tradeData.volume / 1e7 if hasattr(position, 'tradeData') else 0
                trade_side = "BUY" if hasattr(position.tradeData, 'tradeSide') and position.tradeData.tradeSide == 1 else "SELL"

                print(f"Position {position.positionId} ({symbol_name} {trade_side} {volume_lots:.3f}): Floating P&L ${position_pnl:.2f}")

            print(f"Total floating P&L: ${total_floating_pnl:.2f}")
            return total_floating_pnl

        except Exception as e:
            print(f"Error calculating floating P&L: {e}")
            return 0.0

    def _calculate_position_floating_pnl(self, position) -> float:
        """Calculate floating P&L for a single position"""
        try:
            # Method 1: Use swap field as approximation (includes rollover costs)
            # This is the accumulated swap/rollover cost/benefit for the position
            swap_pnl = getattr(position, 'swap', 0) / 100.0  # Convert from cents

            # Method 2: If we had current market prices, we would calculate:
            # For BUY position: (current_price - entry_price) * volume * pip_value
            # For SELL position: (entry_price - current_price) * volume * pip_value

            # Method 3: Use commission field (usually negative)
            commission = getattr(position, 'commission', 0) / 100.0  # Convert from cents

            # For now, use swap as the primary indicator of P&L
            # Swap accumulates daily and reflects the position's performance over time
            # Note: This is not the complete floating P&L, just the swap component

            # In a complete implementation, you would:
            # 1. Get current bid/ask price for the symbol
            # 2. Get position entry price from position.price or tradeData
            # 3. Calculate: (current_price - entry_price) * volume * contract_size * pip_value

            return swap_pnl

        except Exception as e:
            print(f"Error calculating position P&L: {e}")
            return 0.0

    def _close_positions_with_data(self, positions):
        """Close all non-hedge positions across symbols"""
        positions_closed = 0
        for position in positions:
            symbol_name = self._get_symbol_name_from_position(position).upper()
            if symbol_name not in self.hedge_symbols:
                position_id = position.positionId
                print(f"Closing position on {symbol_name} id {position_id}...")
                try:
                    self.trade_client.close_position(position_id, position.tradeData.volume)
                    print(f"Position {position_id} closed.")
                    positions_closed += 1
                except Exception as e:
                    print(f"Error closing position {position_id}: {e}")

        if positions_closed == 0:
            print("No positions found to close (non-hedge)")
        else:
            print(f"Closed {positions_closed} positions (non-hedge)")

    def _start_freeze_period(self):
        """Start the freeze period"""
        self.freeze_start_time = self.get_server_time()
        self.freeze_end_time = self.freeze_start_time + timedelta(minutes=self.freeze_minutes)
        print(f"Freeze period started at {self.freeze_start_time}, duration: {self.freeze_minutes} minutes")

    def check_time_restrictions(self):
        """Check time-based trading restrictions - hedge logic after cutoff"""
        now_ny = self.get_server_time("America/New_York")

        if now_ny.time() >= self.hedge_time:
            current_date = now_ny.date()
            if self.last_hedge_execution_date != current_date:
                self._handle_post_cutoff_positions()
                self.last_hedge_execution_date = current_date

    def _handle_post_cutoff_positions(self):
        """Handle positions after NY cutoff time - create hedge positions if floating loss"""
        try:
            positions = self.trade_client.get_positions_sync()
            self._check_symbols_for_hedge(positions)
        except Exception as e:
            print(f"Error checking positions for hedge: {e}")

    def _check_symbols_for_hedge(self, positions):
        """Check each symbol for hedge requirements"""
        try:
            for symbol in self.allowed_symbols:
                floating_loss = self._get_symbol_floating_loss_with_positions(symbol, positions)
                if floating_loss < 0:
                    print(f"Floating loss detected for {symbol} after cutoff: ${floating_loss:.2f}")
                    print("Creating hedge positions instead of closing...")
                    self._create_hedge_positions_with_positions(symbol, positions)
        except Exception as e:
            print(f"Error checking symbols for hedge: {e}")

    def _get_symbol_floating_loss_with_positions(self, symbol: str, positions) -> float:
        """Get floating P&L for a specific symbol"""
        # Note: Actual P&L calculation requires current market prices
        # For now, return 0 as placeholder
        floating_pnl = 0.0
        symbol = symbol.upper()

        for position in positions:
            symbol_name = self._get_symbol_name_from_position(position)
            if symbol_name.upper() == symbol:
                # Would need current market price to calculate actual P&L
                # For now, assume no floating loss
                pass

        return floating_pnl

    def _create_hedge_positions_with_positions(self, symbol: str, positions):
        """Create hedge positions for the symbol"""
        net_lot_volume = self.calculate_net_lot_volume(symbol.upper(), positions)

        if abs(net_lot_volume) > 0:
            hedge_volume = abs(net_lot_volume)
            volume_in_units = int(hedge_volume * 100000)  # Convert lots to cents

            if net_lot_volume > 0:
                trade_side = 'SELL'
                print(f"Creating SHORT hedge position for {symbol}: {hedge_volume:.3f} lots. Volume in units: {volume_in_units}")
            else:
                trade_side = 'BUY'
                print(f"Creating BUY hedge position for {symbol}: {hedge_volume:.3f} lots. Volume in units: {volume_in_units}")

            # Get symbol info from cache
            symbols_data = getattr(self, '_symbols_data', {})
            symbol_info = symbols_data.get(symbol.upper())
            if not symbol_info:
                print(f"Symbol {symbol} not found in cache")
                return

            try:
                result = self.trade_client.execute_market_order(
                    symbol_id=symbol_info.get('symbolId'),
                    trade_side=trade_side,
                    volume=volume_in_units,
                    comment="Hedge position"
                )
                print(f"Successfully hedge position created for {symbol} to neutralize risk")
            except Exception as e:
                print(f"Failed to place {trade_side} order for {symbol}: {e}")