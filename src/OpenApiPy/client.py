#!/usr/bin/env python

from twisted.internet.endpoints import clientFromString
from twisted.application.internet import ClientService
from protocol import Protocol
from protobuf import Protobuf
from clientProtocolFactory import ClientProtocolFactory
from twisted.internet import reactor, defer

class Client(ClientService):
    def __init__(self, host, port, retryPolicy=None, clock=None, prepareConnection=None, numberOfMessagesToSendPerSecond=5):
        self._runningReactor = reactor
        self.numberOfMessagesToSendPerSecond = numberOfMessagesToSendPerSecond
        endpoint = clientFromString(self._runningReactor, f"ssl:{host}:{port}")
        factory = ClientProtocolFactory.forProtocol(Protocol, client=self)
        super().__init__(endpoint, factory, retryPolicy=retryPolicy, clock=clock, prepareConnection=prepareConnection)
        self._events = dict()
        self._responseDeferreds = dict()
        self.isConnected = False

    def startService(self):
        if self.running:
            return
        deferredWhenConnected = self.whenConnected()
        deferredWhenConnected.addCallbacks(self._connected)
        deferredWhenConnected.addErrback(self._connectFailed)
        ClientService.startService(self)

    def stopService(self):
        if self.running and self.isConnected:
            ClientService.stopService(self)

    def _connected(self, protocol):
        self.isConnected = True
        if hasattr(self, "_connectedCallback"):
            self._connectedCallback(self)

    def _connectFailed(self, failure):
        self.isConnected = False
        if hasattr(self, "_connectFailedCallback"):
            self._connectFailedCallback(self, failure)

    def _disconnected(self):
        self.isConnected = False
        self._responseDeferreds.clear()
        if hasattr(self, "_disconnectedCallback"):
            self._disconnectedCallback(self)

    def _received(self, message):
        if hasattr(self, "_messageReceivedCallback"):
            self._messageReceivedCallback(message)
        if (message.clientMsgId is not None and message.clientMsgId in self._responseDeferreds):
            responseDeferred = self._responseDeferreds[message.clientMsgId]
            self._responseDeferreds.pop(message.clientMsgId)
            responseDeferred.callback(message)

    def send(self, message, msgId=None, responseTimeoutInSeconds=2, **params):
        if type(message) in [str, int]:
            message = Protobuf.get(message, **params)
        responseDeferred = defer.Deferred()
        if msgId is None:
            msgId = str(id(responseDeferred))
        if msgId is not None:
            self._responseDeferreds[msgId] = responseDeferred
        responseDeferred.addErrback(lambda failure: self._onResponseFailure(failure, msgId))
        responseDeferred.addTimeout(responseTimeoutInSeconds, self._runningReactor)
        protocolDiferred = self.whenConnected(failAfterFailures=1)
        protocolDiferred.addCallbacks(lambda protocol: protocol.send(message, msgid=msgId), responseDeferred.errback)
        return responseDeferred

    def setConnectedCallback(self, callback):
        self._connectedCallback = callback

    def setConnectFailedCallback(self, callback):
        self._connectFailedCallback = callback

    def setDisconnectedCallback(self, callback):
        self._disconnectedCallback = callback

    def setMessageReceivedCallback(self, callback):
        self._messageReceivedCallback = callback

    def _onResponseFailure(self, failure, msgId):
        if (msgId is not None and msgId in self._responseDeferreds):
            self._responseDeferreds.pop(msgId)
        return failure
if __name__ == "__main__":
    c = Client("demo.ctraderapi.com", 5035) # Demo connection
    # Callback for getting response of VersionReq
    def onVersionReqResponse(message):
        print("onVersionReqResponse: ", message)
        c.stopService()
    # Callback for getting error of VersionReq 
    def onVersionReqError(failure):
        print("onVersionReqError: ", failure)
        c.stopService()
    # Callback for client connection
    def connected(result):
        print("connected")
        # Client send method will return a Twisted deferred
        #deferred = c.send("VersionReq")
        # Setting the deferred callback and errback
        #deferred.addCallbacks(onVersionReqResponse, onVersionReqError)
    # Callback for client disconnection
    def disconnected(result):
        print("disconnected")
    # Callback for receiving all messages
    def onMessageReceived(message):
        print("Message received: ", message)
    # Setting optional client callbacks
    c.setConnectedCallback(connected)
    c.setDisconnectedCallback(disconnected)
    c.setMessageReceivedCallback(onMessageReceived)
    # Set blocking to false if you don't want to block
    # client will use another thread to run its event loop when blocking is set to false
    c.startService() # optional timeout in seconds
    reactor.run()