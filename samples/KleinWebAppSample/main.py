#!/usr/bin/env python

from klein import Klein
from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from ctrader_open_api.endpoints import EndPoints
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from templates import AddAccountsElement, ClientAreaElement
import json
from twisted.internet import endpoints, reactor
from twisted.web.server import Site
import sys
from twisted.python import log
from twisted.web.static import File
import datetime
from google.protobuf.json_format import MessageToJson
import calendar

host = "localhost"
port = 8080

credentialsFile = open("credentials-dev.json")
credentials = json.load(credentialsFile)
token = ""
currentAccountId = None

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
    global token
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
    if message.payloadType == ProtoHeartbeatEvent().payloadType:
        return
    print("Client Received a Message: \n", message)

authorizedAccounts = []

def setAccount(accountId):
    global currentAccountId
    currentAccountId = int(accountId)
    if accountId not in authorizedAccounts:
        return sendProtoOAAccountAuthReq(accountId)
    return "Account changed successfully"

def sendProtoOAVersionReq(clientMsgId = None):
    request = ProtoOAVersionReq()
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAGetAccountListByAccessTokenReq(clientMsgId = None):
    request = ProtoOAGetAccountListByAccessTokenReq()
    request.accessToken = token
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAAccountLogoutReq(clientMsgId = None):
    request = ProtoOAAccountLogoutReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAAccountAuthReq(clientMsgId = None):
    request = ProtoOAAccountAuthReq()
    request.ctidTraderAccountId = currentAccountId
    request.accessToken = token
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAAssetListReq(clientMsgId = None):
    request = ProtoOAAssetListReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAAssetClassListReq(clientMsgId = None):
    request = ProtoOAAssetClassListReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOASymbolCategoryListReq(clientMsgId = None):
    request = ProtoOASymbolCategoryListReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOASymbolsListReq(includeArchivedSymbols = False, clientMsgId = None):
    request = ProtoOASymbolsListReq()
    request.ctidTraderAccountId = currentAccountId
    request.includeArchivedSymbols = includeArchivedSymbols if type(includeArchivedSymbols) is bool else bool(includeArchivedSymbols)
    deferred = client.send(request)
    deferred.addErrback(onError)
    return deferred

def sendProtoOATraderReq(clientMsgId = None):
    request = ProtoOATraderReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAUnsubscribeSpotsReq(symbolId, clientMsgId = None):
    request = ProtoOAUnsubscribeSpotsReq()
    request.ctidTraderAccountId = currentAccountId
    request.symbolId.append(int(symbolId))
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAReconcileReq(clientMsgId = None):
    request = ProtoOAReconcileReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAGetTrendbarsReq(weeks, period, symbolId, clientMsgId = None):
    request = ProtoOAGetTrendbarsReq()
    request.ctidTraderAccountId = currentAccountId
    request.period = ProtoOATrendbarPeriod.Value(period)
    request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=int(weeks))).utctimetuple())) * 1000
    request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
    request.symbolId = int(symbolId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOAGetTickDataReq(days, quoteType, symbolId, clientMsgId = None):
    request = ProtoOAGetTickDataReq()
    request.ctidTraderAccountId = currentAccountId
    request.type = ProtoOAQuoteType.Value(quoteType.upper())
    request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(days=int(days))).utctimetuple())) * 1000
    request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
    request.symbolId = int(symbolId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOANewOrderReq(symbolId, orderType, tradeSide, volume, price = None, clientMsgId = None):
    request = ProtoOANewOrderReq()
    request.ctidTraderAccountId = currentAccountId
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
    return deferred

def sendNewMarketOrder(symbolId, tradeSide, volume, clientMsgId = None):
    return sendProtoOANewOrderReq(symbolId, "MARKET", tradeSide, volume, clientMsgId = clientMsgId)

def sendNewLimitOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
    return sendProtoOANewOrderReq(symbolId, "LIMIT", tradeSide, volume, price, clientMsgId)

def sendNewStopOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
    return sendProtoOANewOrderReq(symbolId, "STOP", tradeSide, volume, price, clientMsgId)

def sendProtoOAClosePositionReq(positionId, volume, clientMsgId = None):
    request = ProtoOAClosePositionReq()
    request.ctidTraderAccountId = currentAccountId
    request.positionId = int(positionId)
    request.volume = int(volume) * 100
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOACancelOrderReq(orderId, clientMsgId = None):
    request = ProtoOACancelOrderReq()
    request.ctidTraderAccountId = currentAccountId
    request.orderId = int(orderId)
    deferred = client.send(request, clientMsgId = clientMsgId)
    deferred.addErrback(onError)
    return deferred

def sendProtoOADealOffsetListReq(dealId, clientMsgId=None):
    request = ProtoOADealOffsetListReq()
    request.ctidTraderAccountId = currentAccountId
    request.dealId = int(dealId)
    deferred = client.send(request, clientMsgId=clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAGetPositionUnrealizedPnLReq(clientMsgId=None):
    request = ProtoOAGetPositionUnrealizedPnLReq()
    request.ctidTraderAccountId = currentAccountId
    deferred = client.send(request, clientMsgId=clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAOrderDetailsReq(orderId, clientMsgId=None):
    request = ProtoOAOrderDetailsReq()
    request.ctidTraderAccountId = currentAccountId
    request.orderId = int(orderId)
    deferred = client.send(request, clientMsgId=clientMsgId)
    deferred.addErrback(onError)

def sendProtoOAOrderListByPositionIdReq(positionId, fromTimestamp=None, toTimestamp=None, clientMsgId=None):
    request = ProtoOAOrderListByPositionIdReq()
    request.ctidTraderAccountId = currentAccountId
    request.positionId = int(positionId)
    deferred = client.send(request, fromTimestamp=fromTimestamp, toTimestamp=toTimestamp, clientMsgId=clientMsgId)
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
    "ProtoOAReconcileReq": sendProtoOAReconcileReq,
    "ProtoOAGetTrendbarsReq": sendProtoOAGetTrendbarsReq,
    "ProtoOAGetTickDataReq": sendProtoOAGetTickDataReq,
    "NewMarketOrder": sendNewMarketOrder,
    "NewLimitOrder": sendNewLimitOrder,
    "NewStopOrder": sendNewStopOrder,
    "ClosePosition": sendProtoOAClosePositionReq,
    "CancelOrder": sendProtoOACancelOrderReq,
    "DealOffsetList": sendProtoOADealOffsetListReq,
    "GetPositionUnrealizedPnL": sendProtoOAGetPositionUnrealizedPnLReq,
    "OrderDetails": sendProtoOAOrderDetailsReq,
    "OrderListByPositionId": sendProtoOAOrderListByPositionIdReq,
}

def encodeResult(result):
    if type(result) is str:
        return f'{{"result": "{result}"}}'.encode(encoding = 'UTF-8')
    else:
        return MessageToJson(Protobuf.extract(result)).encode(encoding = 'UTF-8')

@app.route('/get-data')
def getData(request):
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    token = request.args.get(b"token", [None])[0]
    result = ""
    if (token is None or token == b""):
        result = "Invalid Token"
    command = request.args.get(b"command", [None])[0]
    if (command is None or command == b""):
        result = f"Invalid Command: {command}"
    commandSplit = command.decode('UTF-8').split(" ")
    print(commandSplit)
    if (commandSplit[0] not in commands):
        result = f"Invalid Command: {commandSplit[0]}"
    else:
        parameters = commandSplit[1:]
        print(parameters)
        result = commands[commandSplit[0]](*parameters)
        result.addCallback(encodeResult)
    if type(result) is str:
        result = encodeResult(result)
    print(result)
    return result

log.startLogging(sys.stdout)

client = Client(EndPoints.PROTOBUF_LIVE_HOST if credentials["Host"].lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
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
