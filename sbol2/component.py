from .constants import *
from .identified import Identified
from .location import Location
from .mapsto import MapsTo
from .measurement import Measurement
from .property import URIProperty, OwnedObject, ReferencedObject


class ComponentInstance(Identified):
    def __init__(self, rdf_type, uri, definition, access, version):
        super().__init__(rdf_type, uri, version)
        self.definition = ReferencedObject(self, SBOL_DEFINITION,
                                           SBOL_COMPONENT_DEFINITION,
                                           '1', '1', [], definition)
        self._access = URIProperty(self, SBOL_ACCESS, '0', '1', [], access)
        self.mapsTos = OwnedObject(self, SBOL_MAPS_TOS, MapsTo,
                                   '0', '*', [])
        self.measurements = OwnedObject(self, SBOL_MEASUREMENTS, Measurement,
                                        '0', '*', [])

    @property
    def access(self):
        return self._access.value

    @access.setter
    def access(self, new_access):
        self._access.set(new_access)


class Component(ComponentInstance):
    def __init__(self, uri=URIRef('example'), definition='',
                 access=SBOL_ACCESS_PUBLIC, version=VERSION_STRING):
        super().__init__(SBOL_COMPONENT, uri, definition, access, version)
        self._roles = URIProperty(self, SBOL_ROLES, '0', '*',
                                  [Component._role_set_role_integration])
        self._roleIntegration = URIProperty(self, SBOL_ROLE_INTEGRATION,
                                            '0', '1', [])
        self.sourceLocations = OwnedObject(self, SBOL_LOCATIONS, Location,
                                           '0', '*', [])

    @property
    def roles(self):
        return self._roles.value

    @roles.setter
    def roles(self, new_roles):
        self._roles.set(new_roles)

    def addRole(self, new_role):
        self._roles.add(new_role)

    def removeRole(self, index=0):
        self._roles.remove(index)

    @property
    def roleIntegration(self):
        return self._roleIntegration.value

    @roleIntegration.setter
    def roleIntegration(self, new_roleIntegration):
        self._roleIntegration.set(new_roleIntegration)

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
        self._direction = URIProperty(self, SBOL_DIRECTION,
                                      '1', '1', [], direction)

    @property
    def direction(self):
        return self._direction.value

    @direction.setter
    def direction(self, new_direction):
        self._direction.set(new_direction)

    def connect(self, interface_component):
        raise NotImplementedError("Not yet implemented")

    def mask(self, masked_component):
        raise NotImplementedError("Not yet implemented")

    def override(selfself, masked_component):
        raise NotImplementedError("Not yet implemented")

    def isMasked(self):
        raise NotImplementedError("Not yet implemented")
