#!/usr/bin/env python

import sys
import unittest
from client import Client
from twisted.internet.defer import timeout

class TestClient(unittest.TestCase):
    """Tests for `OpenApiPy.Client` class."""

    _host = "demo.ctraderapi.com"
    _port = 5035

    def setUp(self):
        self.client = Client(self._host, self._port)
        self.client.start(blocking=False)

    def tearDown(self):
        pass

    def testVersionReq(self):
        def onVersionReqResponse(message):
            self.assertTrue(True, True)
        def onVersionReqError(failure):
            self.assertFail()
        def sendRequest(result):
            deferred = self.client.send("VersionReq")
            deferred.addCallbacks(onVersionReqResponse, onVersionReqError)
        con = self.client.whenConnected(failAfterFailures=1)
        con.addCallback(sendRequest)

if __name__ == "__main__":
    unittest.main()