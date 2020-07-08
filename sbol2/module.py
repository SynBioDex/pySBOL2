from .constants import *
from .identified import Identified
from .mapsto import MapsTo
from .measurement import Measurement
from .property import OwnedObject, ReferencedObject


class Module(Identified):
    def __init__(self, uri='example',
                 # Everything after the asterisk (`*`) is a keyword
                 *, definition='', version=VERSION_STRING,
                 type_uri=SBOL_MODULE):
        super().__init__(type_uri, uri, version)
        self.definition = ReferencedObject(self, SBOL_DEFINITION,
                                           SBOL_MODULE_DEFINITION,
                                           '1', '1', [], definition)
        self.mapsTos = OwnedObject(self, SBOL_MAPS_TOS, MapsTo,
                                   '0', '*', [])
        self.measurements = OwnedObject(self, SBOL_MEASUREMENTS,
                                        Measurement, '0', '*', [])
