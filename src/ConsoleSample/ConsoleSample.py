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
    currentAccountId = None
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
        if message.payloadType in [ProtoOASubscribeSpotsRes().payloadType, ProtoOAAccountLogoutRes().payloadType, ProtoHeartbeatEvent().payloadType]:
            return
        elif message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print("API Application authorized")
            if currentAccountId is not None:
                sendProtoOAAccountAuthReq()
                return
        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            protoOAAccountAuthRes = Protobuf.extract(message)
            print(f"Account {protoOAAccountAuthRes.ctidTraderAccountId} has been authorized")
        else:
            print("Message received: \n", Protobuf.extract(message))
        reactor.callLater(3, callable=executeUserCommand)
    
    def onError(failure): # Call back for errors
        print("Message Error: ", failure)

    def showHelp():
        print("Commands (Parameters with an * are required), ignore the description inside ()")
        print("setAccount(For all subsequent requests this account will be used) *accountId")
        print("ProtoOAVersionReq clientMsgId")
        print("ProtoOAGetAccountListByAccessTokenReq clientMsgId")
        print("ProtoOAAssetListReq clientMsgId")
        print("ProtoOAAssetClassListReq clientMsgId")
        print("ProtoOASymbolCategoryListReq clientMsgId")
        print("ProtoOASymbolsListReq includeArchivedSymbols(True/False) clientMsgId")
        print("ProtoOATraderReq clientMsgId")
        print("ProtoOASubscribeSpotsReq *symbolId *timeInSeconds(Unsubscribes after this time) subscribeToSpotTimestamp(True/False) clientMsgId")
        print("ProtoOAReconcileReq clientMsgId")
        reactor.callLater(3, callable=executeUserCommand)

    def setAccount(accountId):
        global currentAccountId
        if currentAccountId is not None:
            sendProtoOAAccountLogoutReq()
        currentAccountId = int(accountId)
        sendProtoOAAccountAuthReq()

    def sendProtoOAVersionReq(clientMsgId = None):
        request = ProtoOAVersionReq()
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAGetAccountListByAccessTokenReq(clientMsgId = None):
        request = ProtoOAGetAccountListByAccessTokenReq()
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAccountLogoutReq(clientMsgId = None):
        request = ProtoOAAccountLogoutReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAccountAuthReq(clientMsgId = None):
        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = currentAccountId
        request.accessToken = accessToken
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAssetListReq(clientMsgId = None):
        request = ProtoOAAssetListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAAssetClassListReq(clientMsgId = None):
        request = ProtoOAAssetClassListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASymbolCategoryListReq(clientMsgId = None):
        request = ProtoOASymbolCategoryListReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASymbolsListReq(includeArchivedSymbols = False, clientMsgId = None):
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = currentAccountId
        request.includeArchivedSymbols = includeArchivedSymbols if type(includeArchivedSymbols) is bool else bool(includeArchivedSymbols)
        deferred = client.send(request)
        deferred.addErrback(onError)

    def sendProtoOATraderReq(clientMsgId = None):
        request = ProtoOATraderReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOAUnsubscribeSpotsReq(symbolId, clientMsgId = None):
        request = ProtoOAUnsubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    def sendProtoOASubscribeSpotsReq(symbolId, timeInSeconds, subscribeToSpotTimestamp	= False, clientMsgId = None):
        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        request.subscribeToSpotTimestamp = subscribeToSpotTimestamp if type(subscribeToSpotTimestamp) is bool else bool(subscribeToSpotTimestamp)
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)
        reactor.callLater(int(timeInSeconds), sendProtoOAUnsubscribeSpotsReq, symbolId)

    def sendProtoOAReconcileReq(clientMsgId = None):
        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = currentAccountId
        deferred = client.send(request, clientMsgId = clientMsgId)
        deferred.addErrback(onError)

    commands = {
        "help": showHelp,
        "setAccount": setAccount,
        "ProtoOAVersionReq": sendProtoOAVersionReq,
        "ProtoOAGetAccountListByAccessTokenReq": sendProtoOAGetAccountListByAccessTokenReq,
        "ProtoOAAssetListReq": sendProtoOAAssetListReq,
        "ProtoOAAssetClassListReq": sendProtoOAAssetClassListReq,
        "ProtoOASymbolCategoryListReq": sendProtoOASymbolCategoryListReq,
        "ProtoOASymbolsListReq": sendProtoOASymbolsListReq,
        "ProtoOATraderReq": sendProtoOATraderReq,
        "ProtoOASubscribeSpotsReq": sendProtoOASubscribeSpotsReq,
        "ProtoOAReconcileReq": sendProtoOAReconcileReq}

    def executeUserCommand():
        try:
            print("\n")
            userInput = inputimeout("Command (ex help): ", timeout=17)
        except TimeoutOccurred:
            print("Command Input Timeout")
            reactor.callLater(3, callable=executeUserCommand)
            return
        userInputSplit = userInput.split(" ")
        if not userInputSplit:
            print("Command split error: ", userInput)
            reactor.callLater(3, callable=executeUserCommand)
            return
        command = userInputSplit[0]
        try:
            parameters = [parameter if parameter[0] != "*" else parameter[1:] for parameter in userInputSplit[1:]]
        except:
            print("Invalid parameters: ", userInput)
            reactor.callLater(3, callable=executeUserCommand)
        if command in commands:
            commands[command](*parameters)
        else:
            print("Invalid Command: ", userInput)
            reactor.callLater(3, callable=executeUserCommand)

    # Setting optional client callbacks
    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(onMessageReceived)
    # Starting the client service
    client.startService()
    reactor.run()
