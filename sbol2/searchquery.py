from .config import parseNamespace
from .constants import *
from .property import URIProperty, IntProperty, TextProperty
from .toplevel import TopLevel

SEARCH_QUERY_URI: str = PYSBOL2_NS.SearchQuery.toPython()
OBJECT_TYPE_URI: str = PYSBOL2_NS.ObjectType.toPython()
OFFSET_URI: str = PYSBOL2_NS.Offset.toPython()
LIMIT_URI: str = PYSBOL2_NS.Limit.toPython()


class SearchQuery(TopLevel):
    """Search terms to support PartShop advanced search."""
    def __init__(self, search_target: str = SBOL_COMPONENT_DEFINITION,
                 offset: int = 0, limit: int = 25):
        super().__init__(SEARCH_QUERY_URI)
        # Set attributes from TopLevel
        self.displayId = ''
        self.persistentIdentity = ''
        self.version = ''
        # Add some attributes
        self.objectType = URIProperty(self, OBJECT_TYPE_URI, '0', '1', None, search_target)
        self.offset = IntProperty(self, OFFSET_URI, '0', '1', None, offset)
        self.limit = IntProperty(self, LIMIT_URI, '0', '1', None, limit)

    def __setitem__(self, key, value):
        if parseNamespace(key) == '':
            uri = SBOL_URI + '#' + 'key'
        else:
            uri = key
        TextProperty(self, uri, '0', '1', None, value)

    def __getitem__(self, item):
        return self.properties[item][0].toPython()
