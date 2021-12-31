### Client Class

You will use an instance of this class to interact with API.

Each instance of this class will have one connection to API, either live or demo endpoint.

The client class is driven from Twisted ClientService class, and it abstracts away all the connection / reconnection complexities from you.

### Creating a Client

Let's create an isntance of Client class:

```python

from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints

client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

```

It's constructor has several parameters that you can use for controling it behavior:

* host: The API host endpoint, you can use either EndPoints.PROTOBUF_DEMO_HOST or EndPoints.PROTOBUF_LIVE_HOST

* port: The API host port number, you can use EndPoints.PROTOBUF_PORT

* protocol: The protocol that will be used by client for making connections, use imported TcpProtocol

* numberOfMessagesToSendPerSecond: This is the number of messages that will be sent to API per second, set it based on API limitations or leave the default value

There are three other optional parameters which are from Twisted client service, you can find their detail here: https://twistedmatrix.com/documents/current/api/twisted.application.internet.ClientService.html 

### Sending Message

To send a message you have to first create the proto message, ex:

```python
# Import all message types
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *

# ProtoOAApplicationAuthReq message
applicationAuthReq = ProtoOAApplicationAuthReq()
applicationAuthReq.clientId = "Your App Client ID"
applicationAuthReq.clientSecret = "Your App Client secret"

```

After you created the message and populated its fields, you can send it by using Client send method:

```python
deferred = client.send(applicationAuthReq)
```

The client send method returns a Twisted deferred, it will be called when the message response arrived, the callback result will be the response proto message.

If the message send failed, the returned deferred error callback will be called, to handle both cases you can attach two callbacks for getting response or error:

```python
def onProtoOAApplicationAuthRes(result):
	print(result)

def onError(failure):
	print(failure)

deferred.addCallbacks(onProtoOAApplicationAuthRes, onError)
```
For more about Twisted deferreds please check their documentation: https://docs.twistedmatrix.com/en/twisted-16.2.0/core/howto/defer-intro.html

### Canceling Message

You can cancel a message by calling the returned deferred from Client send method Cancel method.

If the message is not sent yet, it will be removed from the messages queue and the deferred Errback method will be called with CancelledError.

If the message is already sent but the response is not received yet, then you will not receive the response and the deferred Errback method will be called with CancelledError.

If the message is already sent and the reponse is received then canceling it's deferred will not have any effect.

### Other Callbacks

The client class has some other optional general purpose callbacks that you can use:

* ConnectedCallback(client): This callback will be called when client gets connected, use client setConnectedCallback method to assign a callback for it

* DisconnectedCallback(client, reason): This callback will be called when client gets disconnected, use client setDisconnectedCallback method to assign a callback for it

* MessageReceivedCallback(client, message): This callback will be called when a message is received, it's called for all message types, use setMessageReceivedCallback to assign a callback for it
