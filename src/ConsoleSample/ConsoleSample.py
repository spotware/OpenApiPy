import sys
sys.path.append('../OpenApiPy')
sys.path.append('../OpenApiPy/messages')
from client import Client
from auth import Auth
from protobuf import Protobuf
from messages.OpenApiCommonModelMessages_pb2 import *
from messages.OpenApiCommonMessages_pb2 import *
from messages.OpenApiMessages_pb2 import *
from messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
import threading
from inputimeout import inputimeout, TimeoutOccurred
import webbrowser

if __name__ == "__main__":
    liveHost = "live.ctraderapi.com"
    demoHost = "demo.ctraderapi.com"
    port = 5035
    hostType = input("Host (Live/Demo): ")
    hostType = hostType.lower()

    while hostType != "live" and  hostType != "demo":
        print(f"{hostType} is not a valid host type.")
        hostType = input("Host (Live/Demo): ")

    appClientId = input("App Client ID: ")
    appClientSecret = input("App Client Secret: ")
    appRedirectUri = input("App Redirect URI: ")
    isTokenAvailable = input("Do you have an access token? (Y/N): ").lower() == "y"

    accessToken = None
    if isTokenAvailable == False:
        auth = Auth(appClientId, appClientSecret, appRedirectUri)
        authUri = auth.getAuthUri()
        print(f"Please continue the authentication on your browser:\n {authUri}")
        webbrowser.open_new(authUri)
        print("\nThen enter the auth code that is appended to redirect URI immediatly (the code is after ?code= in URI)")
        authCode = input("Auth Code: ")
        token = auth.getToken(authCode)
        print("Token: \n", token)
        accessToken = token["accessToken"]
    else:
        accessToken = input("Access Token: ")

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
        elif message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print("API Application authorized")
        elif message.payloadType == ProtoOAGetAccountListByAccessTokenRes().payloadType:
            print("Accounts list received: \n", Protobuf.extract(message))
        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            protoOAAccountAuthRes = Protobuf.extract(message)
            print(f"Account {protoOAAccountAuthRes.ctidTraderAccountId} has been authorized")
        else:
            print("Message received: \n", Protobuf.extract(message))
        reactor.callLater(3, callable=executeUserCommand)
    
    def onError(failure): # Call back for errors
        print("Error: ", failure)

    def showHelp():
        print("Commands (Parameters with an * are required)")
        print("ProtoOAVersionReq clientMsgId")
        print("ProtoOAGetAccountListByAccessTokenReq clientMsgId")
        print("ProtoOAAccountAuthReq *accountId clientMsgId")
        reactor.callLater(3, callable=executeUserCommand)

    def sendProtoOAVersionReq(clientMsgId = None):
        request = ProtoOAVersionReq()
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetAccountListByAccessTokenReq(clientMsgId = None):
        request = ProtoOAGetAccountListByAccessTokenReq()
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAccountAuthReq(accountId, clientMsgId = None):
        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = int(accountId)
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    commands = {
        "help": showHelp,
        "ProtoOAVersionReq": sendProtoOAVersionReq,
        "ProtoOAGetAccountListByAccessTokenReq": sendProtoOAGetAccountListByAccessTokenReq,
        "ProtoOAAccountAuthReq": sendProtoOAAccountAuthReq}

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
        try:
            parameters = [parameter if parameter[0] != "*" else parameter[1:] for parameter in userInputSplit[1:]]
        except:
            print("Invalid parameters: ", userInput)
            reactor.callLater(5, callable=executeUserCommand)
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
