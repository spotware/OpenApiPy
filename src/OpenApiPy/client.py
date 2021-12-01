#!/usr/bin/env python

from twisted.internet.endpoints import clientFromString
from twisted.application.internet import ClientService
from protocol import Protocol
from protobuf import Protobuf
from clientProtocolFactory import ClientProtocolFactory
import threading
from twisted.internet import reactor, defer

class Client(ClientService):
    def __init__(self, host, port, retryPolicy=None, clock=None, prepareConnection=None):
        self._runningReactor = reactor
        endpoint = clientFromString(self._runningReactor, f"ssl:{host}:{port}")
        factory = ClientProtocolFactory.forProtocol(Protocol, client=self)
        super().__init__(endpoint, factory, retryPolicy=retryPolicy, clock=clock, prepareConnection=prepareConnection)
        self._events = dict()

    def start(self, timeout=None, blocking=True):
        def run(timeout):
            self.startService()
            if timeout:
                self._runningReactor.callLater(timeout, self.stop)
            self._runningReactor.run(installSignalHandlers=blocking)
        if blocking:
            run(timeout)
        else:
            self._reactorThread = threading.Thread(target=run,args=(timeout,))
            self._reactorThread.start()

    def stop(self):
        if self.running:
            self.stopService()
        if self._runningReactor.running:
            self._runningReactor.stop()

    def connect(self):
        self._responseDeferreds = dict()
        if hasattr(self, "connectedCallback"):
            self.connectedCallback(self)

    def disconnect(self):
        if hasattr(self, "disconnectedCallback"):
            self.disconnectedCallback(self)

    def receive(self, message):
        if hasattr(self, "messageReceivedCallback"):
            self.messageReceivedCallback(message)
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
        responseDeferred.addTimeout(responseTimeoutInSeconds, self._runningReactor, onTimeoutCancel=lambda result, timeout: self._onResponseTimeout(msgId))
        con = self.whenConnected(failAfterFailures=1)
        con.addCallbacks(lambda protocol: protocol.send(message, msgid=msgId), lambda failure: responseDeferred.errback(failure))
        return responseDeferred

    def setConnectedCallback(self, callback):
        self.connectedCallback = callback

    def setDisconnectedCallback(self, callback):
        self.disconnectedCallback = callback

    def setMessageReceivedCallback(self, callback):
        self.messageReceivedCallback = callback

    def _onResponseTimeout(self, msgId):
        if (msgId is not None and msgId in self._responseDeferreds):
            self._responseDeferreds.pop(msgId)
            raise TimeoutError()