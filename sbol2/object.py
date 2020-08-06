import logging
import posixpath
from typing import List

from deprecated import deprecated
import rdflib
from rdflib import URIRef

from .config import getHomespace, string_equal
from .config import hasHomespace
from .config import Config
from .constants import *
from .property import Property, OwnedObject, URIProperty
from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode
from .uridict import URIDict
from . import SBOL2Serialize
from . import validation


# This is an internal function, not part of the public API
def _compare_properties(obj1, obj2):
    obj1_keys = obj1.properties.keys()
    if sorted(obj1_keys) != sorted(obj2.properties.keys()):
        return False
    # Keys are equal, check values by converting to sets
    for k in obj1_keys:
        if set(obj1.properties[k]) != set(obj2.properties[k]):
            return False
    return True


# This is an internal function, not part of the public API
def _compare_owned_objects(obj1, obj2):
    obj1_keys = obj1.owned_objects.keys()
    if sorted(obj1_keys) != sorted(obj2.owned_objects.keys()):
        return False
    # Keys are equal, check values by converting to dicts
    for k in obj1_keys:
        # Recursively compare child objects
        oo1 = {oo.identity: oo for oo in obj1.owned_objects[k]}
        oo2 = {oo.identity: oo for oo in obj2.owned_objects[k]}
        if oo1.keys() != oo2.keys():
            return False
        for uri in oo1:
            if not oo1[uri].compare(oo2[uri]):
                return False
    return True


class SBOLObject:
    """An SBOLObject converts a Python data structure into an RDF triple store
     and contains methods for serializing and parsing RDF triples.
    """

    def _serialize(self):
        # Convert and SBOL object into RDF triples.
        raise NotImplementedError("Not yet implemented")

    def _nest(self):
        # Pretty-writer that converts flat RDF/XML into nested RDF/XML
        # (ie. SBOL)
        raise NotImplementedError("Not yet implemented")

    def _makeQName(self, uri):
        raise NotImplementedError("Not yet implemented")

    # TODO Docstrings on variables isn't a thing in Python. Consider using Epydoc.
    # The identity property is REQUIRED by all Identified objects
    # and has a data type of URI. A given Identified object's identity
    # URI MUST be globally unique among all other identity URIs.
    # The identity of a compliant SBOL object MUST begin with
    # a URI prefix that maps to a domain over which the user has control.
    # Namely, the user can guarantee uniqueness of identities
    # within this domain. For other best practices regarding URIs
    # see Section 11.2 of the [SBOL specification document
    # (http://sbolstandard.org/wp-content/uploads/2015/08/SBOLv2.0.1.pdf).

    def __init__(self, type_uri=rdflib.URIRef(UNDEFINED),
                 uri=rdflib.URIRef("example")):
        """Open-world constructor."""
        self.owned_objects = URIDict()  # map<rdf_type, vector<SBOLObject>>
        self.properties = URIDict()  # map<rdf_type, vector<SBOLObject>>
        self.doc = None
        self.parent = None
        self._default_namespace = None
        self._hidden_properties = []
        self.rdf_type = str(type_uri)
        self._namespaces = {}
        self.identity = URIProperty(self, SBOL_IDENTITY, '0', '1',
                                    [validation.sbol_rule_10202])
        uri = URIRef(uri)
        if hasHomespace():
            uri = posixpath.join(getHomespace(), uri)
        self.identity = uri

    @property
    def logger(self):
        logger = logging.getLogger('sbol2')
        if not logger.hasHandlers():
            # If there are no handlers, nobody has initialized
            # logging.  Configure logging here so we have a chance of
            # seeing the messages.
            logging.basicConfig()
        return logger

    def __uri__(self) -> rdflib.URIRef:
        """Returns a URIRef representing this object.

        :return: The identity of this object as an rdflib.URIRef
        :rtype: rdflib.URIRef
        """
        return rdflib.URIRef(self.identity)

    @property
    def type(self):
        return self.rdf_type

    @property
    @deprecated(reason='`this` no longer makes sense')
    def this(self):
        # For backward compatibility with pySBOL. Just return myself.
        return self

    def getTypeURI(self):
        """
        :return: The uniform resource identifier that describes
        the RDF-type of this SBOL Object.
        """
        return self.rdf_type

    def getClassName(self, rdf_type):
        """Parses a local class name from the RDF-type of this SBOL Object."""
        if '#' in rdf_type:
            return rdf_type.split('#')[1]
        else:
            return rdf_type

    @deprecated(reason='This is an obsolete carryover from the C++ library')
    def cast(self, cls):
        if not isinstance(self, cls):
            msg = 'Cannot cast instance of {} to class {}'
            msg = msg.format(type(self).__name__, cls.__name__)
            raise TypeError(msg)
        # TODO: libSBOL does a copy here. I don't think that's needed
        # in Python.
        return self

    def find(self, uri):
        """Search this object recursively to see if an object or
        any child object with URI already exists.

        :param uri: The URI to search for.
        :return: The SBOLObject associated with this URI if it exists,
        None otherwise.
        """
        uri = rdflib.URIRef(uri)
        if string_equal(self.identity, uri):
            return self
        for rdf_type, object_store in self.owned_objects.items():
            if rdf_type in self._hidden_properties:
                continue
            for obj in object_store:
                match = obj.find(uri)
                # NOTE: original implementation has 2 recursive calls,
                # which is probably bad...
                if match is not None:
                    return match
        return None

    def cacheObjects(self, objectCache):
        """TODO document

        :param objectCache: a dictionary mapping strings to SBOLObjects
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def find_property(self, uri):
        """Search this object recursively to see if it contains
        a member property with the given RDF type.

        :param uri: The RDF type of the property to search for.
        :return: The SBOLObject that contains a member property
        with the specified RDF type, None otherwise
        """
        if uri in self.owned_objects and uri in self.properties:
            return self
        for rdf_type, object_store in self.owned_objects.items():
            for obj in object_store:
                match = obj.find_property(uri)
                if match:
                    return match
        return None

    def find_property_value(self, uri, value, matches=None):
        """Search this object recursively to see if it contains
        a member property with the given RDF type
        and indicated property value.

        :param uri: The RDF type of the property to search for.
        :param value: The property value to match.
        :param matches:
        :return: A vector containing all objects found that contain
        a member property with the specified RDF type
        """
        matches = []
        for rdf_type, store in self.owned_objects.items():
            # Skip hidden and aliased properties
            if rdf_type in self._hidden_properties:
                continue
            for obj in store:
                matches += obj.find_property_value(uri, value)
        try:
            value_store = self.properties[uri]
            for val in value_store:
                if string_equal(val, value):
                    matches.append(self)
        except KeyError:
            # It is ok that uri is not in properties
            pass
        return matches

    def find_reference(self, uri):
        """Search this object recursively to see if it contains
        a member property with the given RDF type
        and indicated property value.

        :param uri: A URI, either an ontology term or an object reference,
        to search for.
        :return: A vector containing all objects found that contain
        the URI in a property value.
        """
        references = []
        # Ask all the owned objects
        for oo_list in self.owned_objects.values():
            for oo in oo_list:
                references.extend(oo.find_reference(uri))
        # Check myself
        for pvals in self.properties.values():
            if uri in pvals:
                references.append(self)
        return references

    def compare(self, other):
        """Compare two SBOLObjects. The behavior is currently undefined for
        objects with custom annotations or extension classes.

        :param other: The object being compared to this one.
        :return: True if the objects are identical, False if they are different.

        """
        if type(other) != type(self):
            return False
        if self.rdf_type != other.rdf_type:
            return False
        if not _compare_properties(self, other):
            return False
        if not _compare_owned_objects(self, other):
            return False
        return True

    def getPropertyValue(self, property_uri: str) -> str:
        """Get the value of a custom annotation property by its URI.

        :param property_uri: The URI for the property.
        :type property_uri: str
        :return: The value of the property.
        :rtype: str
        :raises: SBOLError(SBOL_ERROR_NOT_FOUND) if property does not exist
        """
        values = self.getPropertyValues(property_uri)
        try:
            return str(values[0])
        except IndexError:
            return ''

    def getPropertyValues(self, property_uri: str) -> List[str]:
        """Get all values of a custom annotation property by its URI.

        :param property_uri: The URI for the property.
        :type property_uri: str
        :return: A vector of property values.
        :rtype: list of strings
        :raises: SBOLError(SBOL_ERROR_NOT_FOUND) if property does not exist
        """
        try:
            return [str(x) for x in self.properties[property_uri]]
        except KeyError as e:
            # no property by this name
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_NOT_FOUND,
                            'Property {} not found'.format(property_uri))

    def getProperties(self):
        """Gets URIs for all properties contained by this object.
        This includes SBOL core properties as well as
        custom annotations. Use this to find custom extension data
        in an SBOL file.

        :return: A vector of URIs that identify the properties contained in this object.
        """
        property_uris = [p for p in self.properties.keys()]
        owned_objects_uris = [p for p in self.owned_objects.keys()]
        return property_uris + owned_objects_uris

    @deprecated(reason='Use extension properties instead')
    def setPropertyValue(self, property_uri, val):
        """Set and overwrite the value for a user-defined annotation property.

        :param property_uri:
        :param val: A string
        :return: None
        """
        if not isinstance(val, str):
            raise TypeError('%r is not a string', val)
        # Ensure that the property is a URIRef
        property_uri = rdflib.URIRef(property_uri)
        # If there is effectively no value (i.e. '') clear out the
        # value
        if not val:
            # No value, no property, do nothing
            if property_uri not in self.properties:
                return
            # If a value exists in the property, set only the first
            # entry to the empty string. This is backward compatible
            # with pySBOL/libSBOL
            if self.properties[property_uri]:
                self.properties[property_uri][0] = rdflib.Literal('')
            return
        # If the value does not exist, just set it and we're done
        if property_uri not in self.properties:
            self.properties[property_uri] = [rdflib.Literal(val)]
            return
        # Ensure that val is a Literal or URIRef
        if not isinstance(val, (rdflib.Literal, rdflib.URIRef)):
            # Default to Literal
            val = rdflib.Literal(val)
            # If an existing property is a URIRef, convert val to URIRef
            if self.properties[property_uri]:
                if isinstance(self.properties[property_uri][0], rdflib.URIRef):
                    val = rdflib.URIRef(val)
        self.properties[property_uri][0] = val

    def addPropertyValue(self, property_uri, val):
        """Append a value to a user-defined annotation property.

        :param property_uri:
        :param val: Either a literal or URI value.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def setAnnotation(self, property_uri, val):
        """Set the value for a user-defined annotation property.
        Synonymous with setPropertyValue.

        :param property_uri:
        :param val: If the value is a URI,
        it should be surrounded by angle brackets,
        else it will be interpreted as a literal value.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def getAnnotation(self, property_uri):
        """Get the value of a custom annotation property by its URI.
        Synonymous with getPropertyValue.

        :param property_uri: The URI for the property.
        :return: The value of the property or SBOL_ERROR_NOT_FOUND.
        """
        raise NotImplementedError("Not yet implemented")

    def apply(self, callback, user_data):
        """
        Recursively call this callback function on the user_data provided
        :param callback: the callback function
        :param user_data: the input to the callback
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def update_uri(self):
        """
        Recursively generates SBOL compliant ids for an object and all
        its owned objects, then checks to make sure that these ids are unique.
        :return: None
        """
        raise NotImplementedError("Implemented by child classes")

    def build_graph(self, graph):
        graph.add((rdflib.URIRef(self.identity),
                   rdflib.RDF.type,
                   rdflib.URIRef(self.rdf_type)))
        for typeURI, proplist in self.properties.items():
            if typeURI in self._hidden_properties:
                # Skip hidden properties
                continue
            if typeURI == SBOL_IDENTITY:
                # Do not write the identity property to SBOL files
                continue
            for prop in proplist:
                graph.add((rdflib.URIRef(self.identity),
                           rdflib.URIRef(typeURI),
                           prop))
        for typeURI, objlist in self.owned_objects.items():
            if typeURI in self._hidden_properties:
                # Skip hidden properties
                continue

            for owned_obj in objlist:
                graph.add((rdflib.URIRef(self.identity),
                           rdflib.URIRef(typeURI),
                           URIRef(owned_obj.identity)))
                owned_obj.build_graph(graph)

            # register ownership relationship in SBOL2Serialize to structure XML
            SBOL2Serialize.register_ownership_relation(self.getTypeURI(),
                                                       typeURI)

    def __str__(self):
        return self.identity

    def is_top_level(self):
        return False

    def __getattribute__(self, name):
        # Call the default method
        result = object.__getattribute__(self, name)
        if isinstance(result, OwnedObject):
            if result.getUpperBound() == '1':
                if result:
                    result = result[0]
                else:
                    result = None
        elif isinstance(result, Property):
            # Else if attribute is any other kind of Property besides
            # OwnedObject, convert so the Property attributes are
            # transparent and look like native types.
            result = result.value
        return result

    def _is_transparent_attribute(self, name):
        try:
            attr = self.__dict__[name]
        except KeyError:
            return False
        return isinstance(attr, Property)

    def _set_transparent_attribute(self, name, value):
        self.__dict__[name].set(value)

    def __setattr__(self, name, value):
        if self._is_transparent_attribute(name):
            self._set_transparent_attribute(name, value)
            return
        object.__setattr__(self, name, value)

    def _added_to_document(self, doc):
        """Classes can override this method to do extra work when
        being added to a document."""
        pass
