from rdflib import URIRef

from .toplevel import TopLevel
from .constants import *
from .property import URIProperty, IntProperty, TextProperty


class Attachment(TopLevel):

    def __init__(self, uri=URIRef("example"),
                 *, type_uri=SBOL_ATTACHMENT, version=VERSION_STRING,
                 source=''):
        super().__init__(type_uri, uri, version)
        self.source = URIProperty(self, SBOL_SOURCE, '1', '1', [], source)
        self.format = URIProperty(self, SBOL_URI + '#format', '0', '1', [])
        self.size = IntProperty(self, SBOL_URI + '#size', '0', '1', [])
        self.hash = TextProperty(self, SBOL_URI + '#hash', '0', '1', [])
