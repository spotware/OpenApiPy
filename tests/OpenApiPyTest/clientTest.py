#!/usr/bin/env python

import sys
sys.path.append('../../src/OpenApiPy')
sys.path.append('../../src/OpenApiPy/messages')

from client import Client
from twisted.internet import reactor
import unittest
from twisted.python.failure import Failure

class ClientTest(unittest.TestCase):
    """Tests for `OpenApiPy.Client` class."""

    _host = "demo.ctraderapi.com"
    _port = 5035

    def setUp(self):
        pass
            

    def tearDown(self):
        pass

    def getClient(self):
        return Client(self._host, self._port)

    def test_Version_Req(self):
        result = None
        client = self.getClient()
        def onResult(res):
            nonlocal result
            result = res
            client.stopService(stopReactor=False)
        deferred = client.send("VersionReq")
        deferred.addBoth(onResult)
        client.startService(blocking=True)  
        self.assertTrue(result is not None and isinstance(result, Failure) is not True) 
        
    def test_App_Auth_Req(self):
        result = None
        client = self.getClient()
        def onResult(res):
            nonlocal result
            result = res
            client.stopService(stopReactor=False)
        deferred = client.send("VersionReq")
        deferred.addBoth(onResult)
        client.startService(blocking=True)
        self.assertTrue(result is not None and isinstance(result, Failure) is not True) 



if __name__ == "__main__":
    unittest.main()