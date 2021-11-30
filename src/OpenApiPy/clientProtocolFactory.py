from twisted.internet.protocol import Factory

class ClientProtocolFactory(Factory):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.client = kwargs['client']

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        p.client = self.client
        return p