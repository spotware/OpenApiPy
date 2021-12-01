from twisted.internet.protocol import ClientFactory

class ClientProtocolFactory(ClientFactory):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.client = kwargs['client']

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        p.client = self.client
        return p