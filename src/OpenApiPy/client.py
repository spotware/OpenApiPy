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
        ClientService.startService(self)

    def stopService(self):
        if self.running and self.isConnected:
            ClientService.stopService(self)

    def _connected(self, protocol):
        self.isConnected = True
        if hasattr(self, "_connectedCallback"):
            self._connectedCallback(protocol)

    def _disconnected(self, reason):
        self.isConnected = False
        self._responseDeferreds.clear()
        if hasattr(self, "_disconnectedCallback"):
            self._disconnectedCallback(reason)

    def _received(self, message):
        if hasattr(self, "_messageReceivedCallback"):
            self._messageReceivedCallback(message)
        if (message.clientMsgId is not None and message.clientMsgId in self._responseDeferreds):
            responseDeferred = self._responseDeferreds[message.clientMsgId]
            self._responseDeferreds.pop(message.clientMsgId)
            responseDeferred.callback(message)

    def send(self, message, clientMsgId=None, responseTimeoutInSeconds=5, **params):
        if type(message) in [str, int]:
            message = Protobuf.get(message, **params)
        responseDeferred = defer.Deferred()
        if clientMsgId is None:
            clientMsgId = str(id(responseDeferred))
        if clientMsgId is not None:
            self._responseDeferreds[clientMsgId] = responseDeferred
        responseDeferred.addErrback(lambda failure: self._onResponseFailure(failure, clientMsgId))
        responseDeferred.addTimeout(responseTimeoutInSeconds, self._runningReactor)
        protocolDiferred = self.whenConnected(failAfterFailures=1)
        protocolDiferred.addCallbacks(lambda protocol: protocol.send(message, clientMsgId=clientMsgId), responseDeferred.errback)
        return responseDeferred

    def setConnectedCallback(self, callback):
        self._connectedCallback = callback

    def setDisconnectedCallback(self, callback):
        self._disconnectedCallback = callback

    def setMessageReceivedCallback(self, callback):
        self._messageReceivedCallback = callback

    def _onResponseFailure(self, failure, msgId):
        if (msgId is not None and msgId in self._responseDeferreds):
            self._responseDeferreds.pop(msgId)
        return failure