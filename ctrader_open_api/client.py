#!/usr/bin/env python

from twisted.internet.endpoints import clientFromString
from twisted.application.internet import ClientService
from ctrader_open_api.protobuf import Protobuf
from ctrader_open_api.factory import Factory
from twisted.internet import reactor, defer


import asyncio
from asyncio import Future

class Client(asyncio.AbstractServer):
    def __init__(self, host, port, protocol, retryPolicy=None, clock=None, prepareConnection=None, numberOfMessagesToSendPerSecond=5):
        self._runningReactor = reactor
        self.numberOfMessagesToSendPerSecond = numberOfMessagesToSendPerSecond
        # endpoint = clientFromString(self._runningReactor, f"ssl:{host}:{port}")
        endpoint = asyncio.open_connection(host, port, ssl=True)
        factory = Factory.forProtocol(protocol, client=self)
        super().__init__(endpoint, factory, retryPolicy=retryPolicy, clock=clock, prepareConnection=prepareConnection)
        self._events = dict()
        self._responseDeferreds = dict()
        self.isConnected = False

    async def startService(self):
        if self.running:
            return
        self.transport, self.protocol = await self.start_serving()

    async def stopService(self):
        if self.running and self.isConnected:
            await self.close()

    def connection_made(self, transport):
        self.transport = transport
        self.isConnected = True
        if hasattr(self, "_connectedCallback"):
            self._connectedCallback(self)

    def connection_lost(self, exc):
        self.isConnected = False
        self._responseDeferreds.clear()
        if hasattr(self, "_disconnectedCallback"):
            self._disconnectedCallback(self, exc)

    def data_received(self, data):
        message = self.factory.protocol.string_received(data)
        if hasattr(self, "_messageReceivedCallback"):
            self._messageReceivedCallback(self, message)
        if (message.clientMsgId is not None and message.clientMsgId in self._responseDeferreds):
            responseDeferred = self._responseDeferreds[message.clientMsgId]
            self._responseDeferreds.pop(message.clientMsgId)
            responseDeferred.set_result(message)

    def send(self, message, clientMsgId=None, responseTimeoutInSeconds=5, **params):
        if type(message) in [str, int]:
            message = Protobuf.get(message, **params)
        responseDeferred = Future()
        if clientMsgId is None:
            clientMsgId = str(id(responseDeferred))
        if clientMsgId is not None:
            self._responseDeferreds[clientMsgId] = responseDeferred
        # responseDeferred.addErrback(lambda failure: self._onResponseFailure(failure, clientMsgId))
        responseDeferred.add_errback(lambda failure: self._onResponseFailure(failure, clientMsgId))
        responseDeferred.add_done_callback(lambda fut: fut.result())
        responseDeferred.add_timeout(responseTimeoutInSeconds, self._runningReactor)
        protocolDiferred = self.whenConnected(failAfterFailures=1)
        protocolDiferred.addCallbacks(lambda protocol: protocol.send(message, clientMsgId=clientMsgId, isCanceled=lambda: clientMsgId not in self._responseDeferreds), responseDeferred.errback)
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

    def _cancelMessageDiferred(self, deferred):
        deferredIdString = str(id(deferred))
        if (deferredIdString in self._responseDeferreds):
            self._responseDeferreds.pop(deferredIdString)
