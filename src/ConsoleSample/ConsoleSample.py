import sys
sys.path.append('../OpenApiPy')
sys.path.append('../OpenApiPy/messages')
from client import Client
from messages.OpenApiCommonModelMessages_pb2 import *
from messages.OpenApiCommonMessages_pb2 import *
from messages.OpenApiMessages_pb2 import *
from messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
import threading
from inputimeout import inputimeout, TimeoutOccurred

if __name__ == "__main__":
    liveHost = "live.ctraderapi.com"
    demoHost = "demo.ctraderapi.com"
    port = 5035
    hostType = input("Host (Live/Demo): ")
    appClientId = input("App Client ID: ")
    appClientSecret = input("App Client Secret: ")

    client = Client(liveHost if hostType.lower() == "live" else demoHost, port) # Demo connection
    
    def connected(_): # Callback for client connection
        print("\nConnected")
        request = ProtoOAApplicationAuthReq()
        request.clientId = appClientId
        request.clientSecret = appClientSecret
        deferred = client.send(request)
        deferred.addErrback(onError)
    
    def disconnected(reason): # Callback for client disconnection
        print("\nDisconnected: ", reason)
    
    def onMessageReceived(message): # Callback for receiving all messages
        if message.payloadType == ProtoHeartbeatEvent().payloadType:
            return
        if message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print("API Application authorized")
        print("Message received: ", message)
        reactor.callLater(3, callable=executeUserCommand)
    
    def onError(failure): # Call back for errors
        print("Error: ", failure)

    def showHelp():
        print("Commands (Parameters with an * are required)")
        print("ProtoOAVersionReq, ex: ProtoOAVersionReq clientMsgId")
        reactor.callLater(3, callable=executeUserCommand)

    def sendProtoOAVersionReq(clientMsgId = None):
        request = ProtoOAVersionReq()
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    commands = {
        "help": showHelp,
        "ProtoOAVersionReq": sendProtoOAVersionReq}

    def executeUserCommand():
        try:
            userInput = inputimeout("Command (ex help): ", timeout=15)
        except TimeoutOccurred:
            reactor.callLater(5, callable=executeUserCommand)
            return
        userInputSplit = userInput.split(" ")
        if not userInputSplit:
            reactor.callLater(5, callable=executeUserCommand)
            return
        command = userInputSplit[0]
        parameters = [parameter if parameter[0] != "*" else parameter[1:] for parameter in userInputSplit[1:]]
        if command in commands:
            commands[command](*parameters)
        else:
            print("Invalid Command: ", userInput)
            reactor.callLater(5, callable=executeUserCommand)

    # Setting optional client callbacks
    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(onMessageReceived)
    # Set blocking to false if you don't want to block
    # client will use another thread to run its event loop when blocking is set to false
    client.startService() # optional timeout in seconds
    reactor.run()
