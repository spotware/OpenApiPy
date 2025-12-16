from ctrader_open_api.bot import Bot


class RiskManagerBot(Bot):
    def on_tick(self, spot_event=None):
        print("on_tick in RiskManagerBot")



if __name__ == "__main__":
    auth = {
        "client_id": "7870_AGNoUDByyfLOPTiKMGwZHQbK5whzvUNo2BpTCsTXff3ajFz8my",
        "client_secret": "0xtJwsbjTul1lmjjOI5rwSaViVIhcMJNqW8bWNzARwHVwQdeuA",
        "account_id": 45416297,
        "account_token": "-KwZawTvJbMvSGaPaQ-Rrt96CltxaiCsWAEK_6IuSDE",
    }

    bot = RiskManagerBot(auth=auth)
    bot.start()