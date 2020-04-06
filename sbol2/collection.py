from .toplevel import TopLevel
from .constants import *
from .property import URIProperty


class Collection(TopLevel):

    def __init__(self, uri=URIRef("example"), version=VERSION_STRING,
                 *, type_uri=SBOL_COLLECTION):
        super().__init__(type_uri, uri, version)
        self._members = URIProperty(self, SBOL_MEMBERS, '0', '*', [])

    @property
    def members(self):
        return self._members.value

    @members.setter
    def members(self, new_members):
        self._members.set(new_members)
