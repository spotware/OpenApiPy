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

log.startLogging(sys.stdout)

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
    print(token)
    if (token is None or token == b""):
        return "Error: Invalid/Empty Token"
    return ClientAreaElement()

def onError(failure):
    print("Message Error: \n", failure)

def connected(client):
    clientType = "Live" if client is liveClient else "Demo"
    print(f"Client {clientType} Connected")
    request = ProtoOAApplicationAuthReq()
    request.clientId = credentials["ClientId"]
    request.clientSecret = credentials["Secret"]
    deferred = client.send(request, clientMsgId = clientType)
    print(f"App auth sent for client {clientType}")
    deferred.addErrback(onError)     

def disconnected(client, reason):
    clientType = "Live" if client is liveClient else "Demo"
    print(f"Client {clientType} Disconnected, reason: \n", reason)

def onMessageReceived(client, message):
    clientType = "Live" if client is liveClient else "Demo"
    print(f"Client {clientType} Received a Message: \n", message)        

def setClientCallbacks(client):
    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(onMessageReceived)

demoClient = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
setClientCallbacks(demoClient)
liveClient = Client(EndPoints.PROTOBUF_LIVE_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
setClientCallbacks(liveClient)

#demoClient.startService()
#liveClient.startService()

endpoint_description = f"tcp6:port={port}:interface={host}"
endpoint = endpoints.serverFromString(reactor, endpoint_description)
site = Site(app.resource())
site.displayTracebacks = True

endpoint.listen(site)
reactor.run()
