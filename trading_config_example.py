#!/usr/bin/env python3
"""
Example trading configurations for the scheduled trader

Copy this file to 'trading_config.py' and customize for your needs
"""

# Trading Configuration Examples

# Example 1: Conservative EURUSD Trading
CONSERVATIVE_CONFIG = {
    "trade_time": "09:00",    # 9 AM daily
    "symbol": "EURUSD",       # Major currency pair
    "volume": 1000,           # 0.01 lots (small position)
    "stop_loss_pips": 20,     # Optional: 20 pip stop loss
    "take_profit_pips": 40,   # Optional: 40 pip take profit
    "comment": "Conservative daily buy"
}

# Example 2: Multiple Daily Trades
MULTIPLE_TRADES_CONFIG = [
    {
        "trade_time": "08:00",
        "symbol": "GBPUSD",
        "volume": 2000,  # 0.02 lots
        "comment": "Morning GBP trade"
    },
    {
        "trade_time": "14:00",
        "symbol": "USDJPY",
        "volume": 1500,  # 0.015 lots
        "comment": "Afternoon JPY trade"
    }
]

# Example 3: Weekly Trading Pattern
WEEKLY_PATTERN_CONFIG = {
    "monday": {"time": "09:00", "symbol": "EURUSD", "volume": 1000},
    "wednesday": {"time": "09:00", "symbol": "GBPUSD", "volume": 1500},
    "friday": {"time": "09:00", "symbol": "USDJPY", "volume": 1000}
}

# Risk Management Settings
RISK_MANAGEMENT = {
    "max_daily_volume": 10000,      # Maximum volume per day (0.1 lots)
    "max_open_positions": 3,        # Maximum concurrent positions
    "emergency_stop": True,         # Enable emergency stop functionality
    "max_daily_loss": 100.0,        # Stop trading if daily loss exceeds this (in account currency)
    "position_size_percent": 2.0    # Risk 2% of account per trade
}

# Notification Settings (optional)
NOTIFICATIONS = {
    "email_enabled": False,
    "email_address": "trader@example.com",
    "telegram_enabled": False,
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "notify_on_trade": True,
    "notify_on_error": True
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": "INFO",           # DEBUG, INFO, WARNING, ERROR
    "log_to_file": True,
    "log_file": "trading_bot.log",
    "max_log_size": "10MB",
    "backup_count": 5
}