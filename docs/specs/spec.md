Doc:

Do research on the pb files in @ctrader_open_api/messages folder, then use openapi to implement

## `TradeClient` class:

Methods:

### __init__: 

Accept a client instance such as 
```python
from ctrader_open_api import Client

def __init__(self, client):
    self._client = client
```
Then you should use the  _client to send request to implement the other following methods

### auth
```python
def auth(self, client_id, secret, account_id, account_token):

# First do application auth
request = ProtoOAApplicationAuthReq()
request.clientId = credentials["ClientId"]
request.clientSecret = credentials["Secret"]
result = client.send(request)

# Then do account auth

request = ProtoOASymbolsListReq()
request.ctidTraderAccountId = credentials["AccountId"]
request.includeArchivedSymbols = False
result = client.send(request)

```


### execute_market_order
### close_position
### get_account_net_profit
### list_positions
### list_orders

## `Bot` class:
Methods:

### __init__
Initialize `TradeClient` instance

### start
invoke client.startService()

### on_tick
print("on_tick")

### on_bar
print("on_bar")