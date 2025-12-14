# XAUUSD Risk Management System Guide

This system continuously monitors your trading account and **automatically closes all XAUUSD positions** as soon as they are detected. It's designed as a risk management tool for traders who want to avoid exposure to gold (XAUUSD) positions.

## ⚠️ CRITICAL WARNINGS

**🚨 AUTOMATIC POSITION CLOSURE 🚨**
- This program **AUTOMATICALLY CLOSES ALL XAUUSD POSITIONS**
- **NO MANUAL CONFIRMATION** - positions are closed immediately when found
- This affects **REAL MONEY** on live accounts
- **TEST THOROUGHLY WITH DEMO ACCOUNT FIRST**
- Have a backup plan if the system fails

## Quick Start

### 1. Install Dependencies

```bash
pip install twisted protobuf
```

### 2. Configure Your Credentials

Ensure your `credentials.json` is set up:

```json
{
    "ClientId": "your_client_id",
    "Secret": "your_client_secret",
    "HostType": "demo",
    "AccessToken": "your_access_token",
    "AccountId": 1234567
}
```

### 3. Run the Risk Manager

```bash
python xauusd_position_manager.py
```

## How It Works

### System Flow
```
Start → Connect → Authenticate → Find XAUUSD Symbol → Start Scanning
  ↓
Every 30 seconds: Scan All Positions → Find XAUUSD → Close Immediately
  ↓
Continue Forever (or until stopped)
```

### Position Detection Process
1. **Reconcile Request**: Gets all open positions from account
2. **Symbol Matching**: Identifies XAUUSD positions by symbol ID
3. **Immediate Closure**: Sends close position request for full volume
4. **Logging**: Records all actions with timestamps

### Example Log Output
```
2024-01-15 10:30:15 - INFO - 🔍 Performing scan #47 at 10:30:15
2024-01-15 10:30:16 - INFO - 📊 Found 3 open positions
2024-01-15 10:30:16 - INFO - 🎯 Found XAUUSD position: ID 12345, BUY, Volume 100000
2024-01-15 10:30:16 - WARNING - 🚨 Closing 1 XAUUSD position(s)
2024-01-15 10:30:16 - INFO - ❌ Closing XAUUSD position 12345 (BUY, 100000 units)
2024-01-15 10:30:17 - INFO - ✅ Successfully closed XAUUSD position 12345
2024-01-15 10:30:17 - INFO - 📊 Total positions closed: 1
```

## Configuration Options

### Basic Settings
```python
# In xauusd_position_manager.py
TARGET_SYMBOL = "XAUUSD"       # Symbol to monitor
SCAN_INTERVAL = 30             # Scan every 30 seconds
```

### Advanced Configuration
Edit the main function to customize:

```python
# Different scan intervals
SCAN_INTERVAL = 10    # More frequent (10 seconds)
SCAN_INTERVAL = 120   # Less frequent (2 minutes)

# Different symbols
TARGET_SYMBOL = "XAGUSD"   # Silver instead of gold
TARGET_SYMBOL = "BTCUSD"   # Bitcoin
```

## Position Closure Details

### What Gets Closed
- **All XAUUSD positions** regardless of:
  - Position size (0.01 lots to 100+ lots)
  - Buy or Sell direction
  - Profit or loss status
  - How long the position has been open

### Closure Method
```python
request = ProtoOAClosePositionReq()
request.ctidTraderAccountId = account_id
request.positionId = position_id
request.volume = full_volume  # Closes entire position
```

### Volume Units
- Positions are closed at full volume
- No partial closures
- Volume is in cTrader's standard units (100,000 = 1.0 lot)

## Monitoring & Statistics

### Real-time Monitoring
The system logs:
- Connection status
- Authentication progress
- Position scans performed
- Positions found and closed
- Errors and issues

### Statistics Tracking
```
📊 Risk Manager Statistics:
   Target Symbol: XAUUSD
   Scan Interval: 30 seconds
   Total Scans: 142
   Positions Closed: 3
   Last Scan: 2024-01-15 14:25:30
   Status: 🟢 Active
```

### Log Files
- **`xauusd_risk_manager.log`**: All activities
- Automatic rotation when files get large
- Timestamped entries for audit trail

## Safety Features

### Built-in Protection
1. **Authentication Checks**: Won't operate without proper authentication
2. **Connection Monitoring**: Pauses if connection is lost
3. **Symbol Validation**: Verifies XAUUSD symbol exists in account
4. **Error Recovery**: Continues scanning after temporary errors
5. **Comprehensive Logging**: Records all actions for review

### Recommended Additional Safety
1. **Position Size Alerts**: Monitor for unusually large positions
2. **Daily Limits**: Set maximum positions to close per day
3. **Market Hours**: Only operate during active trading hours
4. **Backup Monitoring**: Have secondary systems watching

## Use Cases

### 1. Risk Management
- Prevent unwanted XAUUSD exposure
- Automatic cleanup of algorithmic trading errors
- Emergency position closure system

### 2. Account Protection
- Close positions opened by compromise
- Prevent excessive gold exposure
- Automated compliance with trading rules

### 3. Strategy Management
- Enforce "no gold trading" policies
- Clean up after strategy malfunctions
- Maintain portfolio balance

## Troubleshooting

### Common Issues

1. **No Positions Found**
   - Check if positions actually exist
   - Verify symbol name matching (case sensitive)
   - Confirm account has XAUUSD positions

2. **Authentication Failed**
   - Check credentials.json file
   - Verify access token validity
   - Ensure account permissions

3. **Positions Not Closing**
   - Check account balance for margin
   - Verify market is open
   - Review error logs for specific failures

4. **Scanning Stopped**
   - Check network connection
   - Review authentication status
   - Restart the application

### Debug Mode
Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Customization Examples

### Monitor Multiple Symbols
```python
# Modify the system to handle multiple symbols
TARGET_SYMBOLS = ["XAUUSD", "XAGUSD", "BTCUSD"]
```

### Different Scan Frequencies
```python
# For high-frequency monitoring
SCAN_INTERVAL = 5   # Every 5 seconds

# For conservative monitoring
SCAN_INTERVAL = 300 # Every 5 minutes
```

### Conditional Closure
```python
# Only close losing positions
def should_close_position(position):
    current_price = get_current_price(position.tradeData.symbolId)
    entry_price = position.price
    is_losing = (position.tradeData.tradeSide == ProtoOATradeSide.BUY and current_price < entry_price) or \
                (position.tradeData.tradeSide == ProtoOATradeSide.SELL and current_price > entry_price)
    return is_losing
```

## Legal Disclaimer

This risk management system is provided as-is for educational and risk management purposes. Users are responsible for:

- Understanding the implications of automatic position closure
- Testing thoroughly before live use
- Complying with broker terms and conditions
- Managing their own risk appropriately

The author assumes no responsibility for financial losses, missed opportunities, or system failures. Always have backup risk management procedures in place.

## Emergency Procedures

### How to Stop the System
1. **Keyboard Interrupt**: Press `Ctrl+C` in the terminal
2. **Kill Process**: Use task manager or `kill` command
3. **Network Disconnect**: Disconnect internet to stop trading

### Manual Override
If you need to keep XAUUSD positions:
1. Stop the risk manager immediately
2. Disable your API credentials temporarily
3. Modify the code to exclude specific position IDs

### Recovery Procedures
If the system closes positions incorrectly:
1. Review the log files for the exact actions taken
2. Document the issue for analysis
3. Consider manual position recreation if needed
4. Review and adjust the system configuration