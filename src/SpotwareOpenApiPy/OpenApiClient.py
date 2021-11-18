#! /usr/bin/python3.9

import sys

sys.path.append("./messages")

from messages.OpenApiCommonModelMessages_pb2 import *
from messages.OpenApiCommonMessages_pb2 import *
from messages.OpenApiMessages_pb2 import *
from messages.OpenApiModelMessages_pb2 import *

class OpenApiClient:
    def __init__(self, host, port, applicationClientId, applicationClientSecret):
        self.host = host
        self.port = port
        self.applicationClientId = applicationClientId
        self.applicationClientSecret = applicationClientSecret

if __name__ == "__main__":

    client = OpenApiClient("demo.ctraderapi.com",5035,"test","test")
    print(client.applicationClientId)