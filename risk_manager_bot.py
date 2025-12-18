from ctrader_open_api.bot import Bot
from ctrader_open_api.trade_client import TradeClient
from risk_manager import RiskManager
from datetime import time


class RiskManagerBot(Bot):
    def __init__(self, auth):
        super().__init__(auth)

        # Use the TradeClient from Bot base class

        # Risk management configuration
        self.risk_manager = RiskManager(
            trade_client=self.trade_client,
            allowed_symbols=["EURUSD", "GBPUSD", "USDJPY"],  # Configure as needed
            hedge_symbols=["XAUUSD"],  # Configure as needed
            freeze_minutes=60,
            max_lot_volume=0.08,
            loss_threshold=0.01,  # $1000 loss threshold
            hedge_time=time(17, 0),  # 5 PM NY time
            random_trade=False  # Set to True for testing
        )


    def on_tick(self, spot_event=None):
        # print("on_tick in RiskManagerBot")

        try:
            # Only execute risk management if authenticated
            if not self.trade_client.is_authenticated:
                return

            # Execute risk management logic - RiskManager handles async calls internally
            self.risk_manager.act()

        except Exception as e:
            print(f"Error in risk management: {e}")


if __name__ == "__main__":
    auth = {
        "client_id": "7870_AGNoUDByyfLOPTiKMGwZHQbK5whzvUNo2BpTCsTXff3ajFz8my",
        "client_secret": "0xtJwsbjTul1lmjjOI5rwSaViVIhcMJNqW8bWNzARwHVwQdeuA",
        "account_id": 45416297,
        "account_token": "-KwZawTvJbMvSGaPaQ-Rrt96CltxaiCsWAEK_6IuSDE",
    }

    bot = RiskManagerBot(auth=auth)
    bot.start()