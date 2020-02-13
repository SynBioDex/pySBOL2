from abc import ABC, abstractmethod
import collections
import logging
import os
import posixpath

import rdflib
from rdflib import Literal

from .config import Config
from .config import ConfigOptions
from .config import getHomespace
from .config import parseClassName
from .config import parsePropertyName
from .constants import *
from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode


def sort_version(obj):
    return obj.version


class Property(ABC):
    """Member properties of all SBOL objects are defined
    using a Property object.

    The Property class provides a generic interface for accessing SBOL objects.
    At a low level, the Property class converts SBOL data structures
    into RDF triples.
    """

    def __init__(self, property_owner, type_uri, lower_bound, upper_bound,
                 validation_rules, initial_value=None):
        """Construct a Property.

        :param property_owner: All Property objects must have a pointer back
        to their parent SBOLObject.
        :param type_uri: An RDF hash URI for this property, consisting
        of a namespace followed by an identifier.
        For example, Properties of SBOLObjects use URIs of the form
        http://sbols.org/v2#somePropertyName, where the identifier
        somePropertyName determines the appearance of XML nodes
        in an SBOL file. Alternatively, annotations in a custom namespace
        can be provided using a similarly formed hash URI
        in another namespace.
        :param lower_bound:
        :param upper_bound:
        :param validation_rules: A vector of externally defined ValidationRules
        The vector contains pointers to functions which correspond to
        the validation rules listed in the appendix of the formal
        SBOL specification document.  ValidationRules are automatically
        checked every time a setter or adder method is called and
        when Documents are read and written.
        :param initial_value: The initial value of the Property
        (int, str, float supported)
        """
        self._sbol_owner = property_owner
        if isinstance(type_uri, URIRef):
            self._rdf_type = type_uri
        elif isinstance(type_uri, str):
            self._rdf_type = URIRef(type_uri)
        else:
            raise ValueError("RDF type must be URIRef or str")
        self._lowerBound = lower_bound
        self._upperBound = upper_bound
        self._validation_rules = []
        self._validation_rules = validation_rules
        if initial_value is not None:
            self.value = initial_value

    @property
    def logger(self):
        logger = logging.getLogger('sbol')
        if not logger.hasHandlers():
            # If there are no handlers, nobody has initialized
            # logging.  Configure logging here so we have a chance of
            # seeing the messages.
            logging.basicConfig()
        return logger

    def getTypeURI(self):
        """

        :return: URI representing the predicate.
        """
        return self._rdf_type

    def getOwner(self):
        """

        :return: The owner of this Property.
        """
        return self._sbol_owner

    def getRawValue(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return None
        properties = self._sbol_owner.properties[self._rdf_type]
        if self._upperBound == '1':
            try:
                return properties[-1]
            except IndexError:
                # List is empty
                return None
        # upperbound is not 1, just return the list
        return properties

    @property
    def value(self):
        raise NotImplementedError("getter is only implemented by subclasses")

    @value.setter
    def value(self, new_value):
        self.set(new_value)

    @abstractmethod
    def set(self, new_value):
        raise NotImplementedError("set() is only implemented by subclasses")

    @abstractmethod
    def add(self, new_value):
        """Appends the new value to a list of values,
        for properties that allow it."""
        raise NotImplementedError("add() is only implemented by subclasses")

    def remove(self, index):
        """Remove a property value. By default, we assume this is a literal
        located at index 0.
        """
        if self._sbol_owner is not None:
            if self._rdf_type in self._sbol_owner.properties:
                properties = self._sbol_owner.properties[self._rdf_type]
                if index >= len(properties):
                    raise SBOLError('Index out of range',
                                    SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
                if len(properties) == 1:
                    self.clear()
                else:
                    del properties[index]
        else:
            self.logger.error("Unable to update property: SBOL owner not set.")

    def clear(self):
        """Clear all property values."""
        properties = self._sbol_owner.properties[self._rdf_type]
        # current_value = properties[0]
        properties.clear()
        # if isinstance(current_value[0], URIRef):
        #     # this property is a uri
        #     properties.append('<>')
        # elif isinstance(current_value[0], Literal) and current_value[0].datatype == XSD.str:
        #     properties.append('""')

    def write(self):
        """Write property values."""
        subject = self._sbol_owner.identity.get()
        predicate = self._rdf_type
        obj = self.value
        print('Subject: ' + subject)
        print('Predicate: ' + predicate)
        print('Object: ' + obj)

    def find(self, query):
        """Check if a value in this property matches the query."""
        raise NotImplementedError("Not yet implemented")

    def getLowerBound(self):
        return self._lowerBound

    def getUpperBound(self):
        return self._upperBound

    def validate(self, arg):
        if arg is None:
            # NOTE: Original libSBOL code has commented-out code for this case.
            raise TypeError("arg cannot be None")
        for validation_rule in self._validation_rules:
            validation_rule(self._sbol_owner, arg)

    def __contains__(self, item):
        if self.find(item) is not None:
            return True
        else:
            return False

    def _isHidden(self):
        return self._rdf_type in self._sbol_owner.hidden_properties

    def __len__(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return 0
        else:
            properties = self._sbol_owner.properties[self._rdf_type]
            return len(properties)

    def __str__(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return ""
        else:
            return str(self._sbol_owner.properties[self._rdf_type])


class URIProperty(Property):
    @property
    def value(self):
        if self._upperBound == '1':
            return self.getSinglePropertyValue()
        else:
            return self.getPropertyValueList()

    def getSinglePropertyValue(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return None
        properties = self._sbol_owner.properties[self._rdf_type]
        if len(properties) == 0:
            return None
        return properties[-1]

    def getPropertyValueList(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return []
        properties = self._sbol_owner.properties[self._rdf_type]
        if len(properties) == 0:
            return []
        else:
            # Return the whole list
            plist = self._sbol_owner.properties[self._rdf_type]
            new_plist = []
            for p in plist:
                new_plist.append(p.n3()[1:-1])
            return new_plist

    @value.setter
    def value(self, new_value):
        self.set(new_value)

    def set(self, new_value):
        if self.getUpperBound() == '1':
            self.setSinglePropertyValue(new_value)
        else:
            self.setPropertyValueList(new_value)

    def setSinglePropertyValue(self, new_value):
        if type(new_value) is list:
            raise TypeError('The ' + str(self.getTypeURI()) +
                            ' property does not accept list arguments.')
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if new_value is None:
            return
        elif len(self._sbol_owner.properties[self._rdf_type]) == 0:
            self._sbol_owner.properties[self._rdf_type].append(URIRef(new_value))
        else:
            self._sbol_owner.properties[self._rdf_type][-1] = URIRef(new_value)

    def setPropertyValueList(self, new_value_list):
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if new_value_list is None:
            return
        else:
            if type(new_value_list) is list:
                for value in new_value_list:
                    if not isinstance(value, URIRef):
                        self.logger.warning('Value "' + str(value) +
                                            ' assigned to URIProperty ' +
                                            ' is of type ' + str(type(value)) +
                                            '. Wrapping it in: ' + str(URIRef))
                        value = URIRef(value)
                    self._sbol_owner.properties[self._rdf_type].append(value)
            else:
                # the list is actually not a list, but a single element, even
                # though lists are supported.
                self._sbol_owner.properties[self._rdf_type].append(
                    URIRef(new_value_list))

    def add(self, new_value):
        """Appends the new value to a list of values,
        for properties that allow it."""
        if self._sbol_owner is not None:
            if self._rdf_type not in self._sbol_owner.properties:
                self._sbol_owner.properties[self._rdf_type] = []
            properties = self._sbol_owner.properties[self._rdf_type]
            properties.append(URIRef(new_value))
        else:
            self.logger.error("Unable to update property: SBOL owner not set.")


class LiteralProperty(Property):

    def __init__(self, property_owner, type_uri, lower_bound, upper_bound,
                 validation_rules, initial_value=None):
        super().__init__(property_owner, type_uri, lower_bound, upper_bound,
                         validation_rules, initial_value)
        if self.value:
            self.set(self.value)
        #     self._sbol_owner.properties[type_uri] = [initial_value]
        # else:
        #     self._sbol_owner.properties[type_uri] = []

    @property
    def value(self):
        if self._upperBound == '1':
            return self.getSinglePropertyValue()
        else:
            return self.getPropertyValueList()

    def getSinglePropertyValue(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return None
        properties = self._sbol_owner.properties[self._rdf_type]
        if len(properties) == 0:
            return None
        # Just return the object by itself (not a list)
        return properties[-1]

    def getPropertyValueList(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return None
        properties = self._sbol_owner.properties[self._rdf_type]
        return properties.copy()

    @value.setter
    def value(self, new_value):
        self.set(new_value)

    def set(self, new_value):
        if self.getUpperBound() == '1':
            self.setSinglePropertyValue(new_value)
        else:
            self.setPropertyValueList(new_value)

    def setSinglePropertyValue(self, new_value):
        if type(new_value) is list:
            raise TypeError('The ' + str(self.getTypeURI()) +
                            ' property does not accept list arguments.')
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if new_value is None:
            return
        elif len(self._sbol_owner.properties[self._rdf_type]) == 0:
            self._sbol_owner.properties[self._rdf_type].append(Literal(new_value))
        else:
            self._sbol_owner.properties[self._rdf_type][-1] = Literal(new_value)

    def setPropertyValueList(self, new_value_list):
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if new_value_list is None:
            return
        else:
            if type(new_value_list) is list:
                for value in new_value_list:
                    if not isinstance(value, Literal):
                        self.logger.warning('Value "' + str(value) +
                                            ' assigned to LiteralProperty ' +
                                            ' is of type ' + str(type(value)) +
                                            '. Wrapping it in: ' + str(Literal))
                        value = Literal(value)
                    self._sbol_owner.properties[self._rdf_type].append(value)
            else:
                # the list is actually not a list, but a single element, even
                # though lists are supported.
                self._sbol_owner.properties[self._rdf_type].append(URIRef(new_value_list))

    def add(self, new_value):
        if self._sbol_owner is not None:
            if self._rdf_type not in self._sbol_owner.properties:
                self._sbol_owner.properties[self._rdf_type] = []
            properties = self._sbol_owner.properties[self._rdf_type]
            properties.append(Literal(new_value))
        else:
            self.logger.error("Unable to update property: SBOL owner not set.")


class OwnedObject(URIProperty):
    def __init__(self, property_owner, sbol_uri, builder, lower_bound, upper_bound,
                 validation_rules=None, first_object=None):
        """Initialize a container and optionally put the first object in it.
        If validation rules are specified, they will be checked upon initialization.

        builder is a function that takes a single argument, a string,
        and constructs an object of appropriate type for this
        OwnedObject instance. For instance, if this OwnedObject is
        intended to hold ComponentDefinitions, then the builder should
        return an object of type ComponentDefinition.

        """
        super().__init__(property_owner, sbol_uri, lower_bound, upper_bound,
                         validation_rules, first_object)
        if not callable(builder):
            msg = '{!r} object is not callable'
            raise TypeError(msg.format(type(builder)))
        self.builder = builder
        # Register Property in owner Object
        if self._sbol_owner is not None:
            self._sbol_owner.properties.pop(sbol_uri, None)
            self._sbol_owner.owned_objects[sbol_uri] = []  # vector of SBOLObjects
            if first_object is not None:
                self._sbol_owner.owned_objects[sbol_uri].append(first_object)

    def create(self, uri):
        """Creates an instance appropriate for this owned object collection.

        uri - the name of the object

        """
        obj = self.builder(uri=uri)
        self.add(obj)
        return obj

    def add(self, sbol_obj):
        if self._sbol_owner is not None:
            if sbol_obj.is_top_level() and self._sbol_owner.doc is not None:
                self._sbol_owner.doc.add(sbol_obj)
            else:
                object_store = self._sbol_owner.owned_objects[self._rdf_type]
                if sbol_obj in object_store:
                    raise SBOLError("The object " + sbol_obj.identity +
                                    " is already contained by the " +
                                    self._rdf_type + " property",
                                    SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE)
                # Add to Document and check for uniqueness of URI
                if self._sbol_owner.doc is not None:
                    sbol_obj.doc = self._sbol_owner.doc
                sbol_obj.parent = self._sbol_owner
                # Update URI for the argument object and all its children,
                # if SBOL-compliance is enabled.
                sbol_obj.update_uri()
                # Add to parent object
                object_store.append(sbol_obj)
                # Run validation rules
                # TODO

    def __getitem__(self, id):
        if type(id) is int:
            return self.get_int(id)
        if isinstance(id, str):
            return self.get_uri(rdflib.URIRef(id))
        # Anything other than int and str, covered above, is a problem
        errmsg = 'id must be str or int, got {!r}'.format(type(id))
        raise TypeError(errmsg)

    def get_int(self, id):
        object_store = self._sbol_owner.owned_objects[self._rdf_type]
        if id >= len(object_store):
            # Note: for loops expect an IndexError to be
            # raised to properly detect end of sequence
            raise IndexError
        return object_store[id]

    def get_uri(self, id):
        if Config.getOption(ConfigOptions.VERBOSE.value) is True:
            print('SBOL compliant URIs are set to ' +
                  Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value))
            print('SBOL typed URIs are set to ' +
                  Config.getOption(ConfigOptions.SBOL_TYPED_URIS.value))
            print('Searching for ' + id)
        # Search this property's object store for the uri
        object_store = self._sbol_owner.owned_objects[self._rdf_type]
        for obj in object_store:
            if id == obj.identity:
                return obj
        # If searching by the full URI fails, assume the user is searching
        # for an SBOL-compliant URI using the displayId only
        # Form compliant URI for child object
        parent_obj = self._sbol_owner
        resource_namespaces = []
        resource_namespaces.append(getHomespace())
        if parent_obj.doc is not None:
            for ns in parent_obj.doc.resource_namespaces:
                resource_namespaces.append(ns)
        # Check for regular, SBOL-compliant URIs
        obj = self.find_resource(id, resource_namespaces,
                                 object_store, parent_obj, typedURI=False)
        if obj is not None:
            return obj
        else:
            obj = self.find_resource(id, resource_namespaces,
                                     object_store, parent_obj, typedURI=True)
            if obj is not None:
                return obj
            else:
                raise SBOLError('Object ' + id + ' not found',
                                SBOLErrorCode.NOT_FOUND_ERROR)

    def find_resource(self, uri, resource_namespaces, object_store,
                      parent_obj, typedURI=False):
        persistentIdentity = ''
        for ns in resource_namespaces:
            # Assume the parent object is TopLevel and form the compliant URI
            if typedURI is True:
                compliant_uri = posixpath.join(ns, parseClassName(self._rdf_type), uri)
            else:
                compliant_uri = posixpath.join(ns, uri)
            compliant_uri += os.sep
            compliant_uri = URIRef(compliant_uri)
            persistent_id_matches = []
            if Config.getOption('verbose') is True:
                print('Searching for TopLevel: ' + compliant_uri)
            for obj in object_store:
                if compliant_uri in obj.identity:
                    persistent_id_matches.append(obj)
                # Sort objects with same persistentIdentity by version
                # TODO is this right?
                persistent_id_matches.sort(key=sort_version)
            # If objects matching the persistentIdentity were found,
            # return the most recent version
            if len(persistent_id_matches) > 0:
                return persistent_id_matches[-1]
            # Assume the object is not TopLevel # TODO What is this for?
            if SBOL_PERSISTENT_IDENTITY in parent_obj.properties:
                persistentIdentity = parent_obj.properties[SBOL_PERSISTENT_IDENTITY][0]
            if SBOL_VERSION in parent_obj.properties:
                version = parent_obj.properties[SBOL_VERSION][0]
                compliant_uri = posixpath.join(persistentIdentity, uri, version)
            else:
                compliant_uri = posixpath.join(persistentIdentity, uri)
            if Config.getOption(ConfigOptions.VERBOSE.value) is True:
                print('Searching for non-TopLevel: ' + compliant_uri)
            for obj in object_store:
                if obj.identity == compliant_uri:
                    return obj

    def get(self, uri):
        # TODO: orig getter contains a size check when uri is a constant string
        if uri == '':
            return self._sbol_owner.owned_objects[self._rdf_type][0]
        else:
            return self.__getitem__(uri)

    def __setitem__(self, rdf_type, sbol_obj):
        # NOTE: custom implementation. Not sure where this is defined
        # in the original code.
        if self._sbol_owner.is_top_level():
            doc = self._sbol_owner.doc
            if self._isHidden() and doc.find(sbol_obj.identity):
                # In order to avoid a duplicate URI error, don't attempt
                # to add the object if this is a hidden property,
                pass
            else:
                doc.add(sbol_obj)
        # Add to parent object
        if len(self._sbol_owner.owned_objects[rdf_type]) == 0:
            self._sbol_owner.owned_objects[rdf_type].append(sbol_obj)
        else:
            raise SBOLError("Cannot set " + parsePropertyName(rdf_type) +
                            " property. The property is already set. "
                            "Call remove before attempting to "
                            "overwrite the value.",
                            SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
        sbol_obj.parent = self._sbol_owner
        # Update URI for the argument object and all its children,
        # if SBOL-compliance is enabled.
        sbol_obj.update_uri()

        # Run validation rules
        # TODO

    @property
    def value(self):
        if self._upperBound == '1':
            return self.getSinglePropertyValue()
        else:
            return self.getPropertyValueList()

    @value.setter
    def value(self, new_value):
        if new_value is not None:
            self.set(new_value)

    def set(self, sbol_obj):
        """Sets the first object in the container"""
        if self._sbol_owner.is_top_level():
            doc = self._sbol_owner.doc
            if self._isHidden() and doc.find(sbol_obj.identity):
                # In order to avoid a duplicate URI error, don't attempt
                # to add the object if this is a hidden property,
                pass
            else:
                doc.add(sbol_obj)
        self.set_notoplevelcheck(sbol_obj)

    def set_notoplevelcheck(self, sbol_obj):
        # Add to parent object
        if self._rdf_type not in self._sbol_owner.owned_objects:
            self._sbol_owner.owned_objects[self._rdf_type] = []
        if len(self._sbol_owner.owned_objects[self._rdf_type]) == 0:
            self._sbol_owner.owned_objects[self._rdf_type].append(sbol_obj)
        else:
            raise SBOLError("Cannot set " + parsePropertyName(self._rdf_type) +
                            " property. The property is already set. "
                            "Call remove before attempting to "
                            "overwrite the value.",
                            SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
        sbol_obj.parent = self._sbol_owner
        # Update URI for the argument object and all its children,
        # if SBOL-compliance is enabled.
        sbol_obj.update_uri()

        # Run validation rules
        # TODO

    def remove(self, identifier):
        """id can be either an integer index or a string URI"""
        if type(identifier) is int:
            self.removeOwnedObject_int(identifier)
        elif type(identifier) is str:
            self.removeOwnedObject_str(identifier)
        else:
            raise TypeError('id parameter must be an integer index '
                            'or a string uri')

    def removeOwnedObject_int(self, index):
        if self._sbol_owner is not None:
            if self._rdf_type in self._sbol_owner.owned_objects:
                object_store = self._sbol_owner.owned_objects[self._rdf_type]
                if index >= len(object_store):
                    raise SBOLError("Index out of range",
                                    SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
                obj = object_store[index]
                if self._sbol_owner.getTypeURI() == SBOL_DOCUMENT:
                    del obj.doc.SBOLObjects[obj.identity]
                # Erase nested, hidden TopLevel objects from Document
                if obj.doc is not None and obj.doc.find(obj.identity) is not None:
                    obj.doc = None  # TODO not sure what this does
                del object_store[index]
        else:
            raise Exception('This property is not defined in '
                            'the parent object')

    def removeOwnedObject_str(self, uri):
        if self._sbol_owner is not None:
            if self._rdf_type in self._sbol_owner.owned_objects:
                object_store = self._sbol_owner.owned_objects[self._rdf_type]
                for obj in object_store:
                    if uri == obj.identity:
                        object_store.remove(obj)  # TODO is there a better way?
                        # Erase TopLevel objects from Document
                        if self._sbol_owner.getTypeURI() == SBOL_DOCUMENT:
                            del obj.doc.SBOLObjects[uri]
                        # Erase nested, hidden TopLevel objects from Document
                        if obj.doc is not None and obj.doc.find(uri) is not None:
                            obj.doc = None  # TODO not sure what this does
                        return obj

    def clear(self):
        if self._sbol_owner is not None:
            if self._rdf_type in self._sbol_owner.owned_objects:
                object_store = self._sbol_owner.owned_objects[self._rdf_type]
                for obj in object_store:
                    if obj.is_top_level() and obj.doc is not None:
                        obj.doc.SBOLObjects.remove(obj.identity)
                object_store.clear()

    def __len__(self):
        if self._rdf_type not in self._sbol_owner.owned_objects:
            return 0
        else:
            object_store = self._sbol_owner.owned_objects[self._rdf_type]
            return len(object_store)


class ReferencedObject(Property):
    def __init__(self, property_owner, type_uri, reference_type_uri,
                 lower_bound, upper_bound, validation_rules,
                 initial_value=None):
        super().__init__(property_owner, type_uri, lower_bound, upper_bound,
                         validation_rules, initial_value)
        self.reference_type_uri = reference_type_uri
        if self._sbol_owner is not None:
            property_store = []
            self._sbol_owner.properties[type_uri] = property_store

    def get(self, item):
        """Return reference object at this index.
        :param item (int) the index
        """
        reference_store = self._sbol_owner.properties[self._rdf_type]
        return reference_store[item]

    def set(self, new_value):
        if self._sbol_owner is None:
            # Not sure we should raise this, but I'm guessing it would
            # be good to know.
            # TODO: convert this to a better Python exception or to an
            # SBOL exception
            raise Exception('No owner for referenced value')
        if self.getUpperBound() == '1':
            self.setSinglePropertyValue(new_value)
        else:
            self.setPropertyValueList(new_value)

    def _to_uri(self, obj):
        """Converts strings, URIRefs, and sbol.Identified instances into
        rdflib.URIRefs.

        """
        if isinstance(obj, str):
            return rdflib.URIRef(obj)
        if hasattr(obj, '__uri__'):
            # SBOLObjects have a __uri__ method, and others can too
            return obj.__uri__()
        errmsg = 'Cannot convert {} of type {} to a referenced object'
        raise TypeError(errmsg.format(obj, type(obj)))

    def setSinglePropertyValue(self, new_value):
        self._sbol_owner.properties[self._rdf_type] = [self._to_uri(new_value)]

    def setPropertyValueList(self, new_value):
        if hasattr(new_value, '__uri__'):
            # Convert to URI
            # SBOLObjects have a __uri__ method, and others can too
            new_value = new_value.__uri__()
        if isinstance(new_value, str):
            # Turn it into a list
            new_value = [new_value]
        if isinstance(new_value, collections.Iterable):
            # Convert the items to URIRefs
            new_value = list([self._to_uri(x) for x in new_value])
        self._sbol_owner.properties[self._rdf_type] = new_value

    def add(self, uri):
        # Does anyone call this method? If so, it needs to be properly
        # implemented.
        raise Exception('Should ReferencedObject.add be deprecated?')
        if self._sbol_owner is not None:
            self._sbol_owner.properties[self._rdf_type].append(uri)
        else:
            # NOTE: we could raise an exception here, but
            # the original code is not doing anything in this case.
            print('Unable to set item. SBOL owner was None.')

    def addReference(self, uri):
        # Does anyone call this method? If so, it needs to be properly
        # implemented.
        raise Exception('Should ReferencedObject.addReference be deprecated?')
        self._sbol_owner.properties[self._rdf_type].append(uri)

    def _ensure_uri_ref(self, thing):
        """This method ensures that what gets returned is an rdflib.URIRef. If
        the set methods are working properly, this should be
        unnecessary. Hence the warning message if what it finds is not
        a URIRef. The goal is to remove this method eventually.

        """
        if isinstance(thing, rdflib.URIRef):
            return thing
        self.logger.warning('ReferencedObject was not a URIRef: {}'.format(thing))
        return rdflib.URIRef(thing)

    @property
    def value(self):
        raw_value = self.getRawValue()
        if self._upperBound == '1':
            return self._ensure_uri_ref(raw_value)
        else:
            result = [self._ensure_uri_ref(rval) for rval in raw_value]
            # Return a list, not a generator. Consumers are expecting a list.
            return list(result)

    @value.setter
    def value(self, new_value):
        self.set(new_value)
