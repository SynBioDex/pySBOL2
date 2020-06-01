from rdflib import URIRef

from .toplevel import TopLevel
from .constants import *
from .property import URIProperty


class Collection(TopLevel):

    def __init__(self, uri=URIRef("example"), version=VERSION_STRING,
                 *, type_uri=SBOL_COLLECTION):
        super().__init__(type_uri, uri, version)
        self.members = URIProperty(self, SBOL_MEMBERS, '0', '*', [])
