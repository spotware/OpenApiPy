from twisted.internet.defer import timeout
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import clientFromString
from twisted.application.internet import ClientService
from protocol import Protocol
from protobuf import Protobuf
import threading
from twisted.internet import reactor, defer

class Client(ClientService):
    class Protocol(Protocol):
        client = None

        def connectionMade(self):
            super().connectionMade()
            self.client.connect()

        def connectionLost(self, reason):
            super().connectionLost(reason)
            self.client.disconnect()

        def receive(self, message):
            self.client.receive(message)

    class Factory(Factory):
        client = None

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.client = kwargs['client']

        def buildProtocol(self, addr):
            p = super().buildProtocol(addr)
            p.client = self.client
            return p

    def __init__(self, host, port, retryPolicy=None, clock=None, prepareConnection=None):
        self._runningReactor = reactor
        endpoint = clientFromString(self._runningReactor, f"ssl:{host}:{port}")
        factory = Client.Factory.forProtocol(Client.Protocol, client=self)
        super().__init__(endpoint, factory, retryPolicy=retryPolicy, clock=clock, prepareConnection=prepareConnection)
        self._events = dict()
        self.connected = defer.Deferred()
        self.disconnected = defer.Deferred()

    def start(self, timeout=None, blocking=True):
        def run(timeout):
            self.startService()
            if timeout:
                self._runningReactor.callLater(timeout, self.stop)
            self._runningReactor.run(installSignalHandlers=False)
        if blocking:
            run(timeout)
        else:
            self._reactorThread = threading.Thread(target=run,args=(timeout,))
            self._reactorThread.start()

    def stop(self):
        self.stopService()
        if self._runningReactor.running:
            self._runningReactor.stop()

    def connect(self):
        self._responseDeferreds = dict()
        self.connected.callback(self)

    def disconnect(self):
        self.disconnected.callback(self)

    def receive(self, message):
        payload = Protobuf.extract(message)
        kargs = dict(msg=message, msgid=message.clientMsgId,
                     msgtype=message.payloadType,
                     payload=payload,
                     **{fv[0].name: fv[1] for fv in payload.ListFields()})

        if "ctidTraderAccountId" in kargs:
            kargs["ctid"] = payload.ctidTraderAccountId

        if (message.clientMsgId is not None and message.clientMsgId in self._responseDeferreds):
            responseDeferred = self._responseDeferreds[message.clientMsgId]
            self._responseDeferreds.pop(message.clientMsgId)
            responseDeferred.callback(kargs)

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
        con.addCallback(lambda protocol: protocol.send(message, msgid=msgId))

        return responseDeferred

    def _onResponseTimeout(self, msgId):
        if (msgId is not None and msgId in self._responseDeferreds):
            self._responseDeferreds.pop(msgId)
            raise TimeoutError()

if __name__ == "__main__":
    c = Client("demo.ctraderapi.com", 5035) # Demo connection

    def connected(result):
        print("connected")
        deferred = c.send("VersionReq")
        deferred.addCallback(onResponse)
        deferred.addErrback(onError)

    c.connected.addCallback(connected)

    def disconnected(result):
        print("disconnected")

    c.disconnected.addCallback(disconnected)

    def onResponse(result):
        print("Called back Server version: ", result)

    def onError(failure):
        print("Failed")

    # Set blocking to false if you don't want to block
    # client will use another thread to run its event loop when blocking is set to false
    c.start(timeout=6, blocking=False) # optional timeout in seconds