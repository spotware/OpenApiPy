from twisted.web.template import Element, renderer, XMLFile
from twisted.python.filepath import FilePath

class AddAccountsElement(Element):
    loader = XMLFile(FilePath('./markup/add_accounts.xml'))

    def __init__(self, addAccountLink):
        self.addAccountLink = addAccountLink
        super().__init__()

    @renderer
    def addAccountButton(self, request, tag):
        tag.fillSlots(addAccountLink=self.addAccountLink)
        return tag

class ClientAreaElement(Element):
    loader = XMLFile(FilePath('./markup/client_area.xml'))
