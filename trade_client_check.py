# Check trade client
from ctrader_open_api import Client, TcpProtocol, EndPoints
from ctrader_open_api.bot import Bot



def start_bot():
    auth = {
        "client_id": "7870_AGNoUDByyfLOPTiKMGwZHQbK5whzvUNo2BpTCsTXff3ajFz8my",
        "client_secret": "0xtJwsbjTul1lmjjOI5rwSaViVIhcMJNqW8bWNzARwHVwQdeuA",
        "account_id": 45416297,
        "account_token": "-KwZawTvJbMvSGaPaQ-Rrt96CltxaiCsWAEK_6IuSDE",
    }


    bot = Bot(auth=auth)
    bot.start()


if __name__ == "__main__":
    start_bot()