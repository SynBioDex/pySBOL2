from .toplevel import TopLevel
from .constants import *
from .property import URIProperty


class Implementation(TopLevel):

    def __init__(self, uri=URIRef("example"), version=VERSION_STRING,
                 *, type_uri=SBOL_IMPLEMENTATION):
        super().__init__(type_uri, uri, version)
        self._built = URIProperty(self, SBOL_URI+'#built', '0', '1', [])

    @property
    def built(self):
        return self._built.value

    @built.setter
    def built(self, new_built):
        self._built.set(new_built)
