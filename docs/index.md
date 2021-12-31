### Introduction

A Python package for interacting with cTrader Open API.

This package is developed and maintained by Spotware.

You can use OpenApiPy on all kinds of Python apps, it uses Twisted to send and receive messages asynchronously.

Github Repository: https://github.com/spotware/OpenApiPy

### Installation

You can install OpenApiPy from pip:

```
pip install ctrader-open-api
```

### Usage

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

