import datetime
from abc import ABC, abstractmethod
import collections
import logging
import math
import posixpath
from typing import Any, Union

import dateutil.parser
from rdflib import Literal, URIRef
import packaging.version as pv

from .config import Config
from .config import ConfigOptions
from .config import getHomespace
from .config import parseClassName
from .config import parsePropertyName
from .config import string_equal
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

    @staticmethod
    def valid_lower_bound(x: Union[int, float, str]) -> str:
        """Validate the lower bound. Allow numeric strings, ints,
        and floats.
        """
        if isinstance(x, str) and x.isnumeric():
            return x
        elif isinstance(x, int):
            return str(x)
        elif isinstance(x, float) and x.is_integer():
            return str(int(x))
        else:
            raise ValueError('Lower bound must be numeric')

    @staticmethod
    def valid_upper_bound(x: Union[int, float, str]) -> str:
        """Validate the upper bound. Allow numeric strings, ints,
        floats, and '*' (to represent infinity).
        """
        if x == '*':
            return x
        if x is math.inf:
            return '*'
        try:
            x = Property.valid_lower_bound(x)
        except ValueError:
            raise ValueError('Upper bound must be numeric or \'*\'')
        return x

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
        # Ensure property_owner has a properties attribute of type
        # dict. This is a "fail early" check.
        if not isinstance(property_owner.properties, collections.abc.Mapping):
            raise TypeError('property_owner.properties must be a dict')
        self._sbol_owner = property_owner
        self._rdf_type = str(type_uri)
        self._lowerBound = Property.valid_lower_bound(lower_bound)
        self._upperBound = Property.valid_upper_bound(upper_bound)
        # Validate validation rules
        if validation_rules is None:
            # Some constructors pass None for validation rules
            # Convert to empty list
            validation_rules = []
        for vr in validation_rules:
            if not callable(vr):
                raise TypeError('Validation rule %r is not callable' % vr)
        self._validation_rules = validation_rules
        if initial_value is not None:
            self.value = initial_value

    @property
    def logger(self):
        logger = logging.getLogger('sbol2')
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
                    raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                    'Index out of range')
                if len(properties) == 1:
                    self.clear()
                else:
                    del properties[index]
        else:
            self.logger.error("Unable to update property: SBOL owner not set.")

    def clear(self):
        """Clear all property values."""
        properties = self._sbol_owner.properties[self._rdf_type]
        properties.clear()

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
        msg = '{}.find() not yet implemented for query {} of type {}'
        msg = msg.format(type(self).__name__, query, type(query))
        raise NotImplementedError(msg)

    def getLowerBound(self):
        return self._lowerBound

    @property
    def lower_bound(self):
        """Return the lower bound of the property as an integer.

        """
        return int(self._lowerBound)

    def getUpperBound(self):
        return self._upperBound

    @property
    def upper_bound(self):
        """Return the upper bound of the property as a number.  If the upper
        bound is '*', this value is math.inf. Otherwise the upper
        bound is converted to an integer and returned.

        """
        if self._upperBound == '*':
            return math.inf
        return int(self._upperBound)

    def validate(self, arg):
        for validation_rule in self._validation_rules:
            validation_rule(self._sbol_owner, arg)

    def __contains__(self, item):
        try:
            obj = self.find(item)
        except SBOLError as err:
            if err.error_code() == SBOLErrorCode.NOT_FOUND_ERROR:
                return None
            if err.error_code() == SBOLErrorCode.SBOL_ERROR_NOT_FOUND:
                return None
        else:
            return bool(obj)

    def _isHidden(self):
        return self._rdf_type in self._sbol_owner._hidden_properties

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

    @staticmethod
    def guess_args(validators, initial_value):
        """In pysbol there are 4 constructors for each Property. We have
        to figure out which constructor the user intended to call based on
        the arguments. The signatures are:
            IntProperty(owner, rdf_type, low_bound, high_bound, ValidationRules,
                        initial_value)
            IntProperty(owner, rdf_type, low_bound, high_bound, ValidationRules)
            IntProperty(owner, rdf_type, low_bound, high_bound, initial_value)
            IntProperty(owner, rdf_type, low_bound, high_bound)

        We have to guess which of the two 5-arg constructors the user
        intended to call. If both validators and initial_value are None,
        this is the 4-arg constructor, so return None for both. If neither
        validators nor initial_value are None, this is the 6-arg constructor
        so return the values as specified.

        For the 5-arg cases, if the isinstance(initial_value, typeinfo) then
        guess that hte 5th arg is an initial_value. Otherwise assume the 5th
        arg is a list of validation rules.
        """
        if validators is None and initial_value is None:
            # 4-arg constructor
            return None, None
        if initial_value is not None:
            # 6-arg constructor
            return validators, initial_value
        if not isinstance(validators, collections.abc.Iterable):
            # validation rules must be an iterable, like a list,
            # so guess that it is an initial value
            return None, validators
        if all(callable(x) for x in validators):
            # All the values are callable, so guess this is a list of validators
            return validators, None
        # If the 5th arg is not validators, guess that it is an initial value
        return None, validators


class URIProperty(Property):

    def __init__(self, property_owner, type_uri, lower_bound, upper_bound,
                 validation_rules, initial_value=None):
        super().__init__(property_owner, type_uri, lower_bound, upper_bound,
                         validation_rules)
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if initial_value is not None:
            self.validate(initial_value)
            self.value = initial_value

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
        return self.convert_to_user(properties[-1])

    def getPropertyValueList(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return []
        store = self._sbol_owner.properties[self._rdf_type]
        return [self.convert_to_user(x) for x in store]

    @value.setter
    def value(self, new_value):
        self.set(new_value)

    def set(self, new_value):
        self.validate(new_value)
        if self.getUpperBound() == '1':
            self.setSinglePropertyValue(new_value)
        else:
            self.setPropertyValueList(new_value)

    def setSinglePropertyValue(self, new_value):
        new_value = self.convert_from_user(new_value)
        # clear out any old value
        self._sbol_owner.properties[self._rdf_type].clear()
        if new_value is None:
            # We've already cleared the value, do nothing else.
            return
        self._sbol_owner.properties[self._rdf_type].append(new_value)

    def setPropertyValueList(self, value):
        if value is None:
            self._sbol_owner.properties[self._rdf_type] = []
            return
        if isinstance(value, str):
            value = [value]
        if isinstance(value, collections.abc.Iterable):
            new_value = [self.convert_from_user(v) for v in value]
            self._sbol_owner.properties[self._rdf_type] = new_value
            return
        # Unrecognized value. Raise type error
        msg = 'Cannot set URIProperty to value {} of type {}'
        raise TypeError(msg.format(value, type(value).__name__))

    def add(self, new_value):
        # Note: this is only called internally. This method is not
        # accessible from outside the library via the public API.
        self.value += [new_value]

    def convert_to_user(self, value):
        result = str(value)
        if result == '':
            # special case, empty strings are equivalent to None
            return None
        return result

    def convert_from_user(self, value):
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        if not isinstance(value, str):
            msg = '{} values must have type str'.format(self.getTypeURI())
            raise TypeError(msg)
        return URIRef(value)


class LiteralProperty(Property):

    def __init__(self, property_owner, type_uri, lower_bound, upper_bound,
                 validation_rules=None, initial_value=None):
        validation_rules, initial_value = Property.guess_args(validation_rules,
                                                              initial_value)
        super().__init__(property_owner, type_uri, lower_bound, upper_bound,
                         validation_rules)
        if self._rdf_type not in self._sbol_owner.properties:
            self._sbol_owner.properties[self._rdf_type] = []
        if initial_value is not None:
            self.value = initial_value

    @property
    def value(self):
        if self._upperBound == '1':
            return self.getSinglePropertyValue()
        else:
            return self.getPropertyValueList()

    def getSinglePropertyValue(self):
        properties = self._sbol_owner.properties[self._rdf_type]
        if len(properties) == 0:
            return None
        # Just return the object by itself (not a list)
        return self.convert_to_user(properties[0])

    def getPropertyValueList(self):
        properties = self._sbol_owner.properties[self._rdf_type]
        return [self.convert_to_user(v) for v in properties]

    @value.setter
    def value(self, new_value):
        self.set(new_value)

    def set(self, new_value):
        if self.getUpperBound() == '1':
            self.setSinglePropertyValue(new_value)
        else:
            self.setPropertyValueList(new_value)

    def setSinglePropertyValue(self, new_value):
        new_value = self.convert_from_user(new_value)
        # clear out any old value
        self._sbol_owner.properties[self._rdf_type].clear()
        if new_value is None:
            # We've already cleared the value, do nothing else.
            return
        self._sbol_owner.properties[self._rdf_type].append(new_value)

    def setPropertyValueList(self, new_value):
        if not isinstance(new_value, collections.abc.Iterable):
            raise TypeError('{} must be an iterable'.format(self.getTypeURI()))
        # Special case. Should we really support this?
        # Convert a string to a list of that string
        if isinstance(new_value, str):
            new_value = [new_value]
        new_value = [self.convert_from_user(v) for v in new_value]
        # should we filter out None in the list? I don't think so. If
        # the user put them there, then that's what they're going to
        # get.
        self._sbol_owner.properties[self._rdf_type] = new_value

    def add(self, new_value):
        property = self._sbol_owner.properties[self._rdf_type]
        if len(property) >= self.upper_bound:
            msg = 'Property {} has reached the upper bound of {}'
            msg = msg.format(self._rdf_type, self.upper_bound)
            raise ValueError(msg)
        new_value = self.convert_from_user(new_value)
        property.append(new_value)

    def convert_to_user(self, value):
        return str(value)

    def convert_from_user(self, value):
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        if not isinstance(value, str):
            msg = '{} values must have type str'.format(self.getTypeURI())
            raise TypeError(msg)
        return Literal(value)


class IntProperty(LiteralProperty):

    def convert_to_user(self, value):
        return int(value)

    def convert_from_user(self, value):
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        # Convert to int. If conversion fails a ValueError is raised
        value = int(value)
        return Literal(value)


class FloatProperty(LiteralProperty):

    def convert_to_user(self, value: rdflib.Literal) -> float:
        return float(value)

    def convert_from_user(self, value: Any) -> Union[rdflib.Literal, None]:
        """
        :raises: ValueError if value cannot be converted to float
        """
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        # Convert to float. If conversion fails a ValueError is raised
        value = float(value)
        return Literal(value)


class DateTimeProperty(LiteralProperty):

    def convert_to_user(self, value):
        return dateutil.parser.parse(value)

    def convert_from_user(self, value):
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        if isinstance(value, str):
            value = dateutil.parser.parse(value)
        if not isinstance(value, datetime.datetime):
            msg = '{} values must have type datetime'.format(self.getTypeURI())
            raise ValueError(msg)
        return Literal(value)


class TextProperty(LiteralProperty):

    # In the future, pull the convert_to_user and convert_from_user
    # methods out of LiteralProperty and into TextProperty. Then make
    # LiteralProperty an abstract base class.

    def convert_to_user(self, value):
        result = str(value)
        if result == '':
            # special case, empty strings are equivalent to None
            return None
        return result


class OwnedObject(Property):
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
        self.validate(first_object)
        if not callable(builder):
            msg = '{!r} object is not callable'
            raise TypeError(msg.format(type(builder)))
        self.builder = builder
        # Register Property in owner Object
        if self._sbol_owner is not None:
            self._sbol_owner.properties.pop(self._rdf_type, None)
            self._sbol_owner.owned_objects[self._rdf_type] = []  # vector of SBOLObjects
            if first_object is not None:
                self._sbol_owner.owned_objects[self._rdf_type].append(first_object)

    def create(self, uri, builder=None):
        """Creates an instance appropriate for this owned object collection.

        uri - the name of the object

        """
        if not builder:
            builder = self.builder
        else:
            # Override the default builder to create a subtype of the builder, e.g.,
            # create a Range instead of a Location
            if not callable(builder):
                msg = '{!r} object is not callable'
                raise TypeError(msg.format(type(builder)))
            if not issubclass(builder, self.builder):
                msg = '{!r} is not a subclass of {!r}'
                raise TypeError(msg.format(type(builder), type(self.builder)))
        builder_args = dict(uri=uri)
        if self._sbol_owner and hasattr(self._sbol_owner, 'version'):
            builder_args['version'] = self._sbol_owner.version
        obj = builder(**builder_args)
        self.add(obj)
        return obj

    def add(self, sbol_obj):
        if self._sbol_owner is None:
            # Just silently do nothing?
            return

        # If this is a top level object, add it and all its children recursively to the
        # Document. (With some additional refactoring, this could probably all be handled
        # from this method, thus eliminating need for a separate Document adder method)
        if sbol_obj.is_top_level() and self._sbol_owner.doc is not None:
            self._sbol_owner.doc.add(sbol_obj)
            # If a property is hidden, don't return yet, because it still needs to be
            # added as a child object. (By definition, a hidden owned object can be
            # accessed from both the Document top level and as a child of another top
            # level)
            if not self._isHidden():
                return

        # Not top level, add to the attribute
        object_store = self._sbol_owner.owned_objects[self._rdf_type]
        if sbol_obj in object_store:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE,
                            "The object " + sbol_obj.identity +
                            " is already contained by the " +
                            self._rdf_type + " property")
        # Add to Document and check for uniqueness of URI
        if self._sbol_owner.doc is not None:
            sbol_obj.doc = self._sbol_owner.doc
        sbol_obj.parent = self._sbol_owner
        # Update URI for the argument object and all its children,
        # if SBOL-compliance is enabled.
        sbol_obj.update_uri()
        # Check that this URI is unique within the object store
        # See issue #127
        for obj in object_store:
            if obj.identity == sbol_obj.identity:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE,
                                "The object " + sbol_obj.identity +
                                " is already contained by the " +
                                self._rdf_type + " property")
        # Add to parent object
        object_store.append(sbol_obj)
        # Run validation rules
        self.validate(sbol_obj)

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

    def find(self, query):
        if isinstance(query, str):
            try:
                return self.get_uri(rdflib.URIRef(query))
            except SBOLError as e:
                if e.error_code() == SBOLErrorCode.NOT_FOUND_ERROR:
                    return False
                raise
        errmsg = 'Invalid find query {} of type {}'
        errmsg = errmsg.format(query, type(query).__name__)
        raise TypeError(errmsg)

    def get_uri(self, id):
        id = str(id)
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
        # Now assume the search string is a persistent identity
        obj = self.find_persistent_identity(id)
        if obj is not None:
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
                msg = 'Object {} not found'.format(id)
                raise SBOLError(SBOLErrorCode.NOT_FOUND_ERROR, msg)

    def find_persistent_identity(self, search_uri):
        if not Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS):
            # Must be using compliant URIs to search by persistent identity
            return None
        # Search for persistent identity, returning the newest version
        # Similar to the looping in find_resource, but we can do it better
        # if a match, store it. If another match, check versions and keep
        # the newer one.
        found_object = None
        found_version = pv.NegativeInfinity
        object_store = self._sbol_owner.owned_objects[self._rdf_type]
        for obj in object_store:
            if obj.identity.startswith(search_uri):
                obj_version = pv.parse(obj.version)
                if obj_version > found_version:
                    found_object = obj
                    found_version = obj_version
        return found_object

    def find_resource(self, uri, resource_namespaces, object_store,
                      parent_obj, typedURI=False):
        persistentIdentity = ''
        for ns in resource_namespaces:
            # Assume the parent object is TopLevel and form the compliant URI
            #
            # Note the final empty string, which causes a trailing '/'
            # to be added. Not sure why we need the trailing slash,
            # but that's why the '' is there.
            if typedURI is True:
                compliant_uri = posixpath.join(ns, parseClassName(self._rdf_type),
                                               uri, '')
            else:
                compliant_uri = posixpath.join(ns, uri, '')
            compliant_uri = URIRef(compliant_uri)
            persistent_id_matches = []
            if Config.getOption(ConfigOptions.VERBOSE) is True:
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
            if (SBOL_PERSISTENT_IDENTITY in parent_obj.properties
                    and parent_obj.properties[SBOL_PERSISTENT_IDENTITY]):
                persistentIdentity = parent_obj.properties[SBOL_PERSISTENT_IDENTITY][0]
            if (SBOL_VERSION in parent_obj.properties
                    and parent_obj.properties[SBOL_VERSION]):
                version = parent_obj.properties[SBOL_VERSION][0]
                compliant_uri = posixpath.join(persistentIdentity, uri, version)
            else:
                compliant_uri = posixpath.join(persistentIdentity, uri)
            if Config.getOption(ConfigOptions.VERBOSE.value) is True:
                print('Searching for non-TopLevel: ' + compliant_uri)
            for obj in object_store:
                if string_equal(obj.identity, compliant_uri):
                    return obj

    def get(self, uri=''):
        # TODO: orig getter contains a size check when uri is a constant string
        if uri == '':
            object_store = self._sbol_owner.owned_objects[self._rdf_type]
            if object_store:
                return object_store[0]
            else:
                return None
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
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                            "Cannot set " + parsePropertyName(rdf_type) +
                            " property. The property is already set. "
                            "Call remove before attempting to "
                            "overwrite the value.")
        sbol_obj.parent = self._sbol_owner
        # Update URI for the argument object and all its children,
        # if SBOL-compliance is enabled.
        sbol_obj.update_uri()

        # Run validation rules
        self.validate(sbol_obj)

    def convert_to_user(self, value):
        return str(value)

    def getSinglePropertyValue(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return None
        properties = self._sbol_owner.properties[self._rdf_type]
        if len(properties) == 0:
            return None
        return self.convert_to_user(properties[-1])

    def getPropertyValueList(self):
        if self._rdf_type not in self._sbol_owner.properties:
            return []
        store = self._sbol_owner.properties[self._rdf_type]
        return [self.convert_to_user(x) for x in store]

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

    def setSinglePropertyValue(self, new_value):
        # Clear out the previous value, then add the new value
        #
        # TODO: This can leave the attribute empty if `add` fails.
        # Can we capture that and sent the old value back again?
        if new_value is None:
            value = self.get()
            if value is not None:
                self.remove(value.identity)
            return
        self._sbol_owner.owned_objects[self._rdf_type].clear()
        self.add(new_value)

    def setPropertyValueList(self, new_value):
        # Clear out the previous value, then add the new value
        #
        # TODO: This can leave the attribute empty if `add` fails.
        # Can we capture that and sent the old value back again?
        self._sbol_owner.owned_objects[self._rdf_type].clear()
        for nv in new_value:
            self.add(nv)

    def remove(self, identifier):
        """id can be either an integer index or a string URI"""
        if type(identifier) is int:
            return self.removeOwnedObject_int(identifier)
        elif isinstance(identifier, str):
            return self.removeOwnedObject_str(identifier)
        else:
            msg = 'id parameter must be an integer index or a string uri.'
            msg += ' Got {} of type {}'.format(identifier,
                                               type(identifier).__name__)
            raise TypeError(msg)

    def removeOwnedObject_int(self, index):
        if self._sbol_owner is not None:
            if self._rdf_type in self._sbol_owner.owned_objects:
                object_store = self._sbol_owner.owned_objects[self._rdf_type]
                if index >= len(object_store):
                    raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                    "Index out of range")
                obj = object_store[index]
                if self._sbol_owner.getTypeURI() == SBOL_DOCUMENT:
                    del obj.doc.SBOLObjects[rdflib.URIRef(obj.identity)]
                del object_store[index]
                obj.doc = None
                self.validate(None)
                return obj
        else:
            raise Exception('This property is not defined in '
                            'the parent object')

    def removeOwnedObject_str(self, uri):
        if not self._sbol_owner:
            return
        obj = self.find(uri)
        object_store = self._sbol_owner.owned_objects[self._rdf_type]
        object_store.remove(obj)
        # Erase TopLevel objects from Document
        if self._sbol_owner.rdf_type == SBOL_DOCUMENT:
            del obj.doc.SBOLObjects[obj.identity]
        obj.doc = None
        self.validate(None)
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


class ReferencedObject(URIProperty):
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
        if new_value is None or new_value == '':
            self._sbol_owner.properties[self._rdf_type] = []
            return
        self._sbol_owner.properties[self._rdf_type] = [self._to_uri(new_value)]

    def setPropertyValueList(self, new_value):
        if new_value is None:
            self._sbol_owner.properties[self._rdf_type] = []
            return
        if hasattr(new_value, '__uri__'):
            # Convert to URI
            # SBOLObjects have a __uri__ method, and others can too
            new_value = new_value.__uri__()
        if isinstance(new_value, str):
            # Turn it into a list
            new_value = [new_value]
        if isinstance(new_value, collections.abc.Iterable):
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
        if raw_value is None:
            return None
        if self._upperBound == '1':
            return self.convert_to_user(raw_value)
        else:
            # Return a list, not a generator. Consumers are expecting a list.
            return [self.convert_to_user(rval) for rval in raw_value]

    @value.setter
    def value(self, new_value):
        self.set(new_value)
