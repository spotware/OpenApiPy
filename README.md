# OpenApiPy


[![PyPI version](https://badge.fury.io/py/ctrader-open-api.svg)](https://badge.fury.io/py/ctrader-open-api)
![versions](https://img.shields.io/pypi/pyversions/ctrader-open-api.svg)
[![GitHub license](https://img.shields.io/github/license/spotware/OpenApiPy.svg)](https://github.com/spotware/OpenApiPy/blob/main/LICENSE)

A Python package for interacting with cTrader Open API.

This package uses Twisted and it works asynchronously.

- Free software: MIT
- Documentation: https://spotware.github.io/OpenApiPy/.


## Features

* Works asynchronously by using Twisted

* Methods return Twisted deferreds

* It contains the Open API messages files so you don't have to do the compilation

* Makes handling request responses easy by using Twisted deferreds

## Insallation

```
pip install ctrader-open-api
```

# Usage

```python

from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor

hostType = input("Host (Live/Demo): ")
host = EndPoints.PROTOBUF_LIVE_HOST if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

def onError(failure): # Call back for errors
    print("Message Error: ", failure)

def connected(client): # Callback for client connection
    print("\nConnected")
    # Now we send a ProtoOAApplicationAuthReq
    request = ProtoOAApplicationAuthReq()
    request.clientId = "Your application Client ID"
    request.clientSecret = "Your application Client secret"
    # Client send method returns a Twisted deferred
    deferred = client.send(request)
    # You can use the returned Twisted deferred to attach callbacks
    # for getting message response or error backs for getting error if something went wrong
    # deferred.addCallbacks(onProtoOAApplicationAuthRes, onError)
    deferred.addErrback(onError)

def disconnected(client, reason): # Callback for client disconnection
    print("\nDisconnected: ", reason)

def onMessageReceived(client, message): # Callback for receiving all messages
    print("Message received: \n", Protobuf.extract(message))

# Setting optional client callbacks
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)
# Starting the client service
client.startService()
# Run Twisted reactor
reactor.run()

```

Please check documentation or samples for a complete example.

## Dependencies

* <a href="https://pypi.org/project/twisted/">Twisted</a>
* <a href="https://pypi.org/project/protobuf/">Protobuf</a>
