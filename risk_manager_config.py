#!/usr/bin/env python3
"""
Risk Manager Configuration Examples
Customize these settings for your risk management needs
"""

# Basic Configuration
BASIC_CONFIG = {
    "target_symbol": "XAUUSD",      # Symbol to monitor and close
    "scan_interval": 30,            # Scan every 30 seconds
    "credentials_file": "credentials.json",
    "log_level": "INFO"
}

# Advanced Configuration with Multiple Symbols
MULTI_SYMBOL_CONFIG = {
    "target_symbols": ["XAUUSD", "XAGUSD", "BTCUSD"],  # Multiple symbols to monitor
    "scan_interval": 15,            # More frequent scanning
    "credentials_file": "credentials.json",
    "log_level": "INFO",
    "close_immediately": True,      # Close positions as soon as found
    "max_daily_closures": 100       # Safety limit
}

# Conservative Configuration
CONSERVATIVE_CONFIG = {
    "target_symbol": "XAUUSD",
    "scan_interval": 60,            # Less frequent scanning (1 minute)
    "credentials_file": "credentials.json",
    "log_level": "INFO",
    "confirm_before_close": True,   # Add manual confirmation step
    "only_close_losing_positions": True  # Only close positions in loss
}

# Emergency Mode Configuration
EMERGENCY_CONFIG = {
    "target_symbols": ["XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD"],
    "scan_interval": 5,             # Very frequent scanning (5 seconds)
    "credentials_file": "credentials.json",
    "log_level": "DEBUG",
    "close_all_positions": True,    # Close ALL positions regardless of symbol
    "emergency_mode": True
}

# Position Size Limits
SIZE_BASED_CONFIG = {
    "target_symbol": "XAUUSD",
    "scan_interval": 30,
    "credentials_file": "credentials.json",
    "log_level": "INFO",
    "max_position_size": 1000000,   # Only close positions larger than 1.0 lot
    "min_position_size": 10000,     # Only close positions smaller than 0.1 lot
    "size_based_closure": True
}

# Time-Based Risk Management
TIME_BASED_CONFIG = {
    "target_symbol": "XAUUSD",
    "scan_interval": 30,
    "credentials_file": "credentials.json",
    "log_level": "INFO",
    "active_hours": {
        "start": "09:00",           # Only active during market hours
        "end": "17:00",
        "timezone": "UTC"
    },
    "weekend_mode": "pause",        # Pause scanning on weekends
    "news_blackout": True          # Pause during major news events
}

# Notification Settings
NOTIFICATION_CONFIG = {
    "email_alerts": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "recipients": ["trader@example.com"]
    },
    "telegram_alerts": {
        "enabled": True,
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    },
    "webhook_alerts": {
        "enabled": True,
        "url": "https://your-webhook-url.com/alerts"
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_to_file": True,
    "log_file": "xauusd_risk_manager.log",
    "max_log_size": "50MB",
    "backup_count": 10,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "separate_error_log": True,
    "error_log_file": "xauusd_errors.log"
}

# Safety Limits
SAFETY_CONFIG = {
    "max_daily_closures": 50,       # Max positions to close per day
    "max_hourly_closures": 10,      # Max positions to close per hour
    "cooldown_after_closure": 60,   # Wait 60 seconds after closing position
    "emergency_stop_loss": 1000.0,  # Stop if total daily loss exceeds this
    "position_size_limits": {
        "max_size": 10000000,       # Don't close positions larger than 10 lots
        "min_size": 1000           # Don't close positions smaller than 0.01 lots
    }
}

# Demo vs Live Account Settings
ACCOUNT_SETTINGS = {
    "demo_account": {
        "credentials_file": "credentials_demo.json",
        "aggressive_closure": True,  # More aggressive on demo
        "scan_interval": 10
    },
    "live_account": {
        "credentials_file": "credentials_live.json",
        "conservative_closure": True,  # More careful on live
        "scan_interval": 60,
        "require_confirmation": True
    }
}