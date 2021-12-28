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
from templates import AddAccountsElement
import json
import os

host = "localhost"
port = 8080

credentialsFile = open("credentials-dev.json")
credentials = json.load(credentialsFile)
auth = Auth(credentials["ClientId"], credentials["Secret"], f"http://{host}:{port}/redirect")
authUri = auth.getAuthUri()

app = Klein()

@app.route('/')
def root(request):
    return flattenString(None, AddAccountsElement(authUri))

@app.route('/redirect')
def redirect(request):
    authCode = request.args.get(b"code", [None])[0]
    if (authCode is not None):
        print(f"Code: {authCode}")
        token = auth.getToken(authCode)
        if "errorCode" in token and token["errorCode"] is not None:
            return f'Error: {token["description"]}'
        else:
            return f'Access Token: {token["access_token"]}'
    else:
        return "Invalid Auth Code"

app.run(host, port)
