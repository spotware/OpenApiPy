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

hostType = input("Host (Live/Demo): ")
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
