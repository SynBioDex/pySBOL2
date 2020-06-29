from rdflib import URIRef

from .constants import *
from .identified import Identified
from .measurement import Measurement
from .property import URIProperty, ReferencedObject, OwnedObject


class Participation(Identified):

    def __init__(self, type_uri=SBOL_PARTICIPATION, uri=URIRef('example'),
                 participant='', version=VERSION_STRING):
        super().__init__(type_uri, uri, version)
        self.roles = URIProperty(self, SBOL_ROLES, '0', '*', [])
        self.participant = ReferencedObject(self, SBOL_PARTICIPANT,
                                            SBOL_FUNCTIONAL_COMPONENT,
                                            '1', '1', [], participant)
        self.measurements = OwnedObject(self, SBOL_MEASUREMENTS,
                                        Measurement, '0', '*', [])

    def addRole(self, new_role):
        val = self.roles
        val.append(new_role)
        self.roles = val

    def removeRole(self, index=0):
        val = self.roles
        del val[index]
        self.roles = val

    def define(self, species, role=""):
        raise NotImplementedError('Not yet implemented')
