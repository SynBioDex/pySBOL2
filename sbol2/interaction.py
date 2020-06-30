from .constants import *
from .component import FunctionalComponent
from .identified import Identified
from .measurement import Measurement
from .participation import Participation
from .property import OwnedObject
from .property import URIProperty
from . import validation


class Interaction(Identified):
    def __init__(self, uri='example', interaction_type=SBO_INTERACTION,
                 *, type_uri=SBOL_INTERACTION, version=VERSION_STRING):
        super().__init__(type_uri=type_uri, uri=uri, version=version)
        self.functionalComponents = OwnedObject(self,
                                                SBOL_FUNCTIONAL_COMPONENTS,
                                                FunctionalComponent,
                                                '0', '*', [validation.libsbol_rule_18])
        self.types = URIProperty(self, SBOL_TYPES,
                                 '1', '*', [], interaction_type)
        self.participations = OwnedObject(self, SBOL_PARTICIPATIONS,
                                          Participation,
                                          '0', '*', [])
        self.measurements = OwnedObject(self, SBOL_MEASUREMENTS,
                                        Measurement, '0', '*', [])
