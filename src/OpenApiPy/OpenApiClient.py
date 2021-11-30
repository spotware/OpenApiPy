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
        responseDeferred.addTimeout(responseTimeoutInSeconds, self._runningReactor, onTimeoutCancel=lambda result, timeout: self._onResponseTimeout(msgId, timeout))
        con = self.whenConnected(failAfterFailures=1)
        con.addCallbacks(lambda protocol: protocol.send(message, msgid=msgId), lambda failure: responseDeferred.errback(failure))
        return responseDeferred

    def setConnectedCallback(self, callback):
        self.connectedCallback = callback

    def setDisconnectedCallback(self, callback):
        self.disconnectedCallback = callback

    def setMessageReceivedCallback(self, callback):
        self.messageReceivedCallback = callback

    def _onResponseTimeout(self, msgId, timeout):
        if (msgId is not None and msgId in self._responseDeferreds):
            self._responseDeferreds.pop(msgId)
            raise TimeoutError()

if __name__ == "__main__":
    c = Client("demo.ctraderapi.com", 5035) # Demo connection
    # Callback for getting response of VersionReq
    def onVersionReqResponse(message):
        print("onVersionReqResponse: ", message)
    # Callback for getting error of VersionReq 
    def onVersionReqError(failure):
        print("onVersionReqError: ", failure)
    # Callback for client connection
    def connected(result):
        print("connected")
        # Client send method will return a Twisted deferred
        deferred = c.send("VersionReq")
        # Setting the deferred callback and errback
        deferred.addCallbacks(onVersionReqResponse, onVersionReqError)
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
    c.start(timeout=6, blocking=False) # optional timeout in seconds