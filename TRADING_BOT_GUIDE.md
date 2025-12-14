# Scheduled Trading Bot Guide

This guide shows you how to create an automated trading bot that opens buy positions every day at 9 AM using the cTrader Open API.

## ⚠️ IMPORTANT WARNINGS

**🚨 REAL MONEY TRADING 🚨**
- This bot trades with **REAL MONEY** on live markets
- **Test thoroughly with demo account first**
- Set appropriate position sizes to limit risk
- Monitor trades regularly
- Have a risk management strategy
- Never risk more than you can afford to lose

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_scheduler.txt
```

### 2. Configure Your Credentials

Make sure your `credentials.json` file is set up with your cTrader Open API credentials:

```json
{
    "ClientId": "your_client_id",
    "Secret": "your_client_secret",
    "HostType": "demo",
    "AccessToken": "your_access_token",
    "AccountId": 1234567
}
```

### 3. Run the Trading Bot

```bash
python scheduled_trader.py
```

## Configuration

Edit the configuration in `scheduled_trader.py`:

```python
# Configuration
TRADE_TIME = "09:00"  # Time to execute daily trades (24-hour format)
SYMBOL = "EURUSD"     # Trading symbol
VOLUME = 1000         # Position size (1000 = 0.01 lots)
```

## How It Works

### 1. Connection & Authentication
```
Client Start → Connect to cTrader → Authenticate App → Authenticate Account → Get Symbols
```

### 2. Scheduling
- Uses Python `schedule` library to trigger trades at specific times
- Runs in background thread alongside cTrader client
- Logs all activities to `trading_bot.log`

### 3. Order Execution
When the scheduled time arrives:
1. Check connection and authentication status
2. Create a `ProtoOANewOrderReq` with:
   - Market order type (executes immediately)
   - Buy side (long position)
   - Specified volume
   - Target symbol

### 4. Order Structure
```python
request = ProtoOANewOrderReq()
request.ctidTraderAccountId = account_id
request.symbolId = symbol_id
request.orderType = ProtoOAOrderType.MARKET  # Immediate execution
request.tradeSide = ProtoOATradeSide.BUY     # Buy/Long position
request.volume = 1000  # Position size in smallest units
```

## Volume Units

cTrader uses volume in **smallest units**:
- 1000 units = 0.01 lots (micro lot)
- 10000 units = 0.1 lots (mini lot)
- 100000 units = 1.0 lot (standard lot)

## Customization Options

### Different Order Types

```python
# Market Order (immediate execution)
request.orderType = ProtoOAOrderType.MARKET

# Limit Order (buy at specific price)
request.orderType = ProtoOAOrderType.LIMIT
request.limitPrice = 1.1050

# Stop Order (buy when price rises above level)
request.orderType = ProtoOAOrderType.STOP
request.stopPrice = 1.1100
```

### Risk Management

```python
# Add Stop Loss and Take Profit
request.stopLoss = 1.1000      # Exit if price drops to this level
request.takeProfit = 1.1200    # Exit if price rises to this level

# Add comment for tracking
request.comment = "Daily scheduled buy"
```

### Multiple Symbols/Times

```python
# Schedule multiple trades
schedule.every().day.at("09:00").do(lambda: create_order("EURUSD", 1000))
schedule.every().day.at("14:00").do(lambda: create_order("GBPUSD", 1500))
schedule.every().day.at("20:00").do(lambda: create_order("USDJPY", 2000))
```

## Demo vs Live Trading

### Demo Account (Recommended for Testing)
```json
{
    "HostType": "demo"
}
```
- Uses virtual money
- Same market conditions as live
- Perfect for testing strategies

### Live Account (Real Money)
```json
{
    "HostType": "live"
}
```
- **Uses real money**
- Real profit and loss
- **Only use after thorough testing**

## Monitoring & Logging

### Log File
All activities are logged to `trading_bot.log`:
```
2024-01-15 09:00:01 - INFO - ⏰ Executing scheduled trade...
2024-01-15 09:00:02 - INFO - 🛒 Creating BUY market order for EURUSD
2024-01-15 09:00:03 - INFO - ✅ Market buy order created successfully!
```

### Real-time Monitoring
The bot outputs status to console:
- Connection status
- Authentication progress
- Order execution
- Error messages

## Safety Features

### Built-in Checks
1. **Authentication Verification**: Won't trade if not properly authenticated
2. **Symbol Validation**: Verifies symbol exists before trading
3. **Connection Status**: Checks connection before executing orders
4. **Error Handling**: Comprehensive error logging and handling

### Recommended Additional Safety
1. **Position Size Limits**: Never risk more than 1-2% of account per trade
2. **Daily Loss Limits**: Stop trading if daily losses exceed threshold
3. **Market Hours**: Only trade during active market hours
4. **News Awareness**: Avoid trading during major news events

## Example Usage Scenarios

### 1. Simple Daily Buy Strategy
- Buy EURUSD every day at 9 AM
- Small position size (0.01 lots)
- Let positions run until manually closed

### 2. Scalping Strategy
- Multiple small trades per day
- Quick entries and exits
- Tight stop losses

### 3. Swing Trading
- Daily entries with stop loss and take profit
- Hold positions for several days
- Larger position sizes

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check credentials.json file
   - Verify access token is valid
   - Ensure account ID is correct

2. **Symbol Not Found**
   - Symbol name must match exactly
   - Check if symbol is available in your account
   - Some symbols may not be available in demo accounts

3. **Order Rejected**
   - Insufficient funds
   - Market closed
   - Symbol not tradeable
   - Position size too small/large

### Getting Help

1. Check the log file for detailed error messages
2. Review cTrader Open API documentation
3. Test with demo account first
4. Start with small position sizes

## Legal Disclaimer

This trading bot is provided for educational purposes. Trading involves substantial risk of loss and is not suitable for all investors. The author is not responsible for any financial losses incurred through the use of this software. Please trade responsibly and never risk more than you can afford to lose.