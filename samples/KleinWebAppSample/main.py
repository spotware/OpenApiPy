#!/usr/bin/env python

from klein import run, route
from klein import Klein, Plating
from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from ctrader_open_api.endpoints import EndPoints
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.web.template import tags, slot, flattenString
from random import Random
from templates import AddAccountsElement, ClientAreaElement
import json
import os
from twisted.logger import Logger
from twisted.internet import endpoints, reactor
from twisted.web.server import Site
import sys
from twisted.python import log
from twisted.web.static import File
from twisted.web import resource
import datetime

host = "localhost"
port = 8080

credentialsFile = open("credentials-dev.json")
credentials = json.load(credentialsFile)

auth = Auth(credentials["ClientId"], credentials["Secret"], f"http://{host}:{port}/redirect")
authUri = auth.getAuthUri()
app = Klein()

@app.route('/')
def root(request):
    return AddAccountsElement(authUri)

@app.route('/redirect')
def redirect(request):
    authCode = request.args.get(b"code", [None])[0]
    if (authCode is not None and authCode != b""):
        token = auth.getToken(authCode)
        if "errorCode" in token and token["errorCode"] is not None:
            return f'Error: {token["description"]}'
        else:
            return request.redirect(f'/client-area?token={token["access_token"]}')
    else:
        return "Error: Invalid/Empty Auth Code"

@app.route('/client-area')
def clientArea(request):
    token = request.args.get(b"token", [None])[0]
    if (token is None or token == b""):
        return "Error: Invalid/Empty Token"
    return ClientAreaElement()

@app.route('/css/', branch=True)
def css(request):
    return File("./css")

@app.route('/js/', branch=True)
def js(request):
    return File("./js")

def onError(failure):
    print("Message Error: \n", failure)

def connected(client):
    print("Client Connected")
    request = ProtoOAApplicationAuthReq()
    request.clientId = credentials["ClientId"]
    request.clientSecret = credentials["Secret"]
    deferred = client.send(request)
    deferred.addErrback(onError)     

def disconnected(client, reason):
    print("Client Disconnected, reason: \n", reason)

def onMessageReceived(client, message):
    print("Client Received a Message: \n", message)        

authorizedAccounts = []

def setAccount(accountId):
    if accountId in authorizedAccounts:
        sendProtoOAAccountLogoutReq(accountId)
    sendProtoOAAccountAuthReq(accountId)

def sendProtoOAVersionReq(clientMsgId = None):
    request = ProtoOAVersionReq()
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAGetAccountListByAccessTokenReq(accessToken, clientMsgId = None):
    request = ProtoOAGetAccountListByAccessTokenReq()
    request.accessToken = accessToken
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAAccountLogoutReq(accountId, clientMsgId = None):
    request = ProtoOAAccountLogoutReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAAccountAuthReq(accountId, accessToken, clientMsgId = None):
    request = ProtoOAAccountAuthReq()
    request.ctidTraderAccountId = accountId
    request.accessToken = accessToken
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAAssetListReq(accountId, clientMsgId = None):
    request = ProtoOAAssetListReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAAssetClassListReq(accountId, clientMsgId = None):
    request = ProtoOAAssetClassListReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOASymbolCategoryListReq(accountId, clientMsgId = None):
    request = ProtoOASymbolCategoryListReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOASymbolsListReq(accountId, includeArchivedSymbols = False, clientMsgId = None):
    request = ProtoOASymbolsListReq()
    request.ctidTraderAccountId = accountId
    request.includeArchivedSymbols = includeArchivedSymbols if type(includeArchivedSymbols) is bool else bool(includeArchivedSymbols)
    deferred = client.send(request)
    deferred.addErrback(onError)

def sendProtoOATraderReq(accountId, clientMsgId = None):
    request = ProtoOATraderReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAUnsubscribeSpotsReq(accountId, symbolId, clientMsgId = None):
    request = ProtoOAUnsubscribeSpotsReq()
    request.ctidTraderAccountId = accountId
    request.symbolId.append(int(symbolId))
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOASubscribeSpotsReq(accountId, symbolId, timeInSeconds, subscribeToSpotTimestamp	= False, clientMsgId = None):
    request = ProtoOASubscribeSpotsReq()
    request.ctidTraderAccountId = accountId
    request.symbolId.append(int(symbolId))
    request.subscribeToSpotTimestamp = subscribeToSpotTimestamp if type(subscribeToSpotTimestamp) is bool else bool(subscribeToSpotTimestamp)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    reactor.callLater(int(timeInSeconds), sendProtoOAUnsubscribeSpotsReq, symbolId)

def sendProtoOAReconcileReq(accountId, clientMsgId = None):
    request = ProtoOAReconcileReq()
    request.ctidTraderAccountId = accountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAGetTrendbarsReq(accountId, weeks, period, symbolId, clientMsgId = None):
    request = ProtoOAGetTrendbarsReq()
    request.ctidTraderAccountId = accountId
    request.period = ProtoOATrendbarPeriod.Value(period)
    request.fromTimestamp = int((datetime.datetime.utcnow() - datetime.timedelta(weeks=int(weeks))).timestamp()) * 1000
    request.toTimestamp = int(datetime.datetime.utcnow().timestamp()) * 1000
    request.symbolId = int(symbolId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAGetTickDataReq(accountId, days, quoteType, symbolId, clientMsgId = None):
    request = ProtoOAGetTickDataReq()
    request.ctidTraderAccountId = accountId
    request.type = ProtoOAQuoteType.Value(quoteType.upper())
    request.fromTimestamp = int((datetime.datetime.utcnow() - datetime.timedelta(days=int(days))).timestamp()) * 1000
    request.toTimestamp = int(datetime.datetime.utcnow().timestamp()) * 1000
    request.symbolId = int(symbolId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOANewOrderReq(accountId, symbolId, orderType, tradeSide, volume, price = None, clientMsgId = None):
    request = ProtoOANewOrderReq()
    request.ctidTraderAccountId = accountId
    request.symbolId = int(symbolId)
    request.orderType = ProtoOAOrderType.Value(orderType.upper())
    request.tradeSide = ProtoOATradeSide.Value(tradeSide.upper())
    request.volume = int(volume) * 100
    if request.orderType == ProtoOAOrderType.LIMIT:
        request.limitPrice = float(price)
    elif request.orderType == ProtoOAOrderType.STOP:
        request.stopPrice = float(price)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendNewMarketOrder(symbolId, tradeSide, volume, clientMsgId = None):
    sendProtoOANewOrderReq(symbolId, "MARKET", tradeSide, volume, clientMsgId = clientMsgId)

def sendNewLimitOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
    sendProtoOANewOrderReq(symbolId, "LIMIT", tradeSide, volume, price, clientMsgId)

def sendNewStopOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
    sendProtoOANewOrderReq(symbolId, "STOP", tradeSide, volume, price, clientMsgId)

def sendProtoOAClosePositionReq(accountId, positionId, volume, clientMsgId = None):
    request = ProtoOAClosePositionReq()
    request.ctidTraderAccountId = accountId
    request.positionId = int(positionId)
    request.volume = int(volume) * 100
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

def sendProtoOACancelOrderReq(accountId, orderId, clientMsgId = None):
    request = ProtoOACancelOrderReq()
    request.ctidTraderAccountId = accountId
    request.orderId = int(orderId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)

commands = {
        "setAccount": setAccount,
        "ProtoOAVersionReq": sendProtoOAVersionReq,
        "ProtoOAGetAccountListByAccessTokenReq": sendProtoOAGetAccountListByAccessTokenReq,
        "ProtoOAAssetListReq": sendProtoOAAssetListReq,
        "ProtoOAAssetClassListReq": sendProtoOAAssetClassListReq,
        "ProtoOASymbolCategoryListReq": sendProtoOASymbolCategoryListReq,
        "ProtoOASymbolsListReq": sendProtoOASymbolsListReq,
        "ProtoOATraderReq": sendProtoOATraderReq,
        "ProtoOASubscribeSpotsReq": sendProtoOASubscribeSpotsReq,
        "ProtoOAReconcileReq": sendProtoOAReconcileReq,
        "ProtoOAGetTrendbarsReq": sendProtoOAGetTrendbarsReq,
        "ProtoOAGetTickDataReq": sendProtoOAGetTickDataReq,
        "NewMarketOrder": sendNewMarketOrder,
        "NewLimitOrder": sendNewLimitOrder,
        "NewStopOrder": sendNewStopOrder,
        "ClosePosition": sendProtoOAClosePositionReq,
        "CancelOrder": sendProtoOACancelOrderReq}

@app.route('/get-data')
def getData(request):
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    token = request.args.get(b"token", [None])[0]
    result = ""
    if (token is None or token == b""):
        result = "Invalid Token"
    command = request.args.get(b"command", [None])[0]
    if (command is None or command == b"" or command not in commands):
        result = "Invalid Command"
    else:
        result = commands[command]()
    return f'{{"result": "{result}"}}'.encode(encoding = 'UTF-8')

#hostType = input("Host (Live/Demo): ")
hostType = "demo"
hostType = hostType.lower()

while hostType != "live" and  hostType != "demo":
    print(f"{hostType} is not a valid host type.")
    hostType = input("Host (Live/Demo): ")

log.startLogging(sys.stdout)

client = Client(EndPoints.PROTOBUF_LIVE_HOST if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)
client.startService()

endpoint_description = f"tcp6:port={port}:interface={host}"
endpoint = endpoints.serverFromString(reactor, endpoint_description)
site = Site(app.resource())
site.displayTracebacks = True

endpoint.listen(site)
reactor.run()
