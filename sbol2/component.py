from rdflib import URIRef

from .constants import *
from .identified import Identified
from .location import OwnedLocation
from .mapsto import MapsTo
from .measurement import Measurement
from .property import URIProperty, OwnedObject, ReferencedObject


class ComponentInstance(Identified):
    def __init__(self, type_uri, uri, definition, access, version):
        super().__init__(type_uri, uri, version)
        self.definition = ReferencedObject(self, SBOL_DEFINITION,
                                           SBOL_COMPONENT_DEFINITION,
                                           '1', '1', [], definition)
        self.access = URIProperty(self, SBOL_ACCESS, '0', '1', [], access)
        self.mapsTos = OwnedObject(self, SBOL_MAPS_TOS, MapsTo,
                                   '0', '*', [])
        self.measurements = OwnedObject(self, SBOL_MEASUREMENTS, Measurement,
                                        '0', '*', [])


class Component(ComponentInstance):
    def __init__(self, uri=URIRef('example'), definition='',
                 access=SBOL_ACCESS_PUBLIC, version=VERSION_STRING):
        super().__init__(SBOL_COMPONENT, uri, definition, access, version)
        self.roles = URIProperty(self, SBOL_ROLES, '0', '*',
                                 [Component._role_set_role_integration])
        self.roleIntegration = URIProperty(self, SBOL_ROLE_INTEGRATION,
                                           '0', '1', [])
        self.sourceLocations = OwnedLocation(self, SBOL_SOURCE_LOCATIONS, '0', '*')

    def addRole(self, new_role):
        val = self.roles
        val.append(new_role)
        self.roles = val

    def removeRole(self, index=0):
        val = self.roles
        del val[index]
        self.roles = val

    @staticmethod
    def _role_set_role_integration(sbol_obj, arg):
        """SBOL 2.3.0 says that if a Component has roles then it
        MUST specify a roleIntegration.
        """
        if not isinstance(sbol_obj, Component):
            raise TypeError('{!r} is not of type Component'.format(sbol_obj))
        if arg:
            if not sbol_obj.roleIntegration:
                # If roles are specified and no roleIntegration is present
                # default to mergeRoles
                sbol_obj.roleIntegration = SBOL_ROLE_INTEGRATION_MERGE


class FunctionalComponent(ComponentInstance):
    def __init__(self, uri=URIRef('example'), definition='',
                 access=SBOL_ACCESS_PUBLIC, direction=SBOL_DIRECTION_NONE,
                 version=VERSION_STRING):
        super().__init__(SBOL_FUNCTIONAL_COMPONENT, uri,
                         definition, access, version)
        self.direction = URIProperty(self, SBOL_DIRECTION,
                                     '1', '1', [], direction)

    def connect(self, interface_component):
        raise NotImplementedError("Not yet implemented")

    def mask(self, masked_component):
        raise NotImplementedError("Not yet implemented")

    def override(selfself, masked_component):
        raise NotImplementedError("Not yet implemented")

    def isMasked(self):
        raise NotImplementedError("Not yet implemented")
