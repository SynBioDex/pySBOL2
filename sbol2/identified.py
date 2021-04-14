import posixpath
from typing import Union

from rdflib import URIRef

from .object import SBOLObject
from .config import Config
from .config import ConfigOptions
from .config import getHomespace
from .config import hasHomespace
from .constants import *
from .property import ReferencedObject, TextProperty
from .property import URIProperty
from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode
from .config import parseClassName
from . import validation
from .versionproperty import VersionProperty


class Identified(SBOLObject):
    # The persistentIdentity property is OPTIONAL and has a data type of URI.
    # This URI serves to uniquely refer to a set of SBOL objects
    # that are different versions of each other.
    # An Identified object MUST be referred to
    # using either its identity URI or its persistentIdentity URI.
    # _persistentIdentity = None

    # The displayId property is an OPTIONAL identifier
    # with a data type of String.
    # This property is intended to be an intermediate
    # between name and identity that is machine-readable,
    # but more human-readable than the full URI
    # of an identity. If the displayId property is used,
    # then its String value SHOULD be locally unique
    # (global uniqueness is not necessary)
    # and MUST be composed of only alphanumeric or underscore characters
    # and MUST NOT begin with a digit.
    # _displayId = None

    # If the version property is used,
    # then it is RECOMMENDED that version numbering follow the conventions
    # of [semantic versioning](http://semver.org/),
    # particularly as implemented by [Maven](http://maven.apache.org/).
    # This convention represents versions as sequences
    # of numbers and qualifiers that are separated
    # by the characters '.' and '-' and are compared in lexicographical order
    # (for example, 1 < 1.3.1 < 2.0-beta).
    # For a full explanation, see the linked resources.
    # _version = None
    version: Union[str, VersionProperty]

    # The wasDerivedFrom property is OPTIONAL and has a data type of URI.
    # An SBOL object with this property refers to another SBOL object
    # or non-SBOL resource from which this object was derived.
    # If the wasDerivedFrom property of an SBOL object A
    # that refers to an SBOL object B has an identical persistentIdentity,
    # and both A and B have a version,
    # then the version of B MUST precede that of A.
    # In addition, an SBOL object MUST NOT refer to itself
    # via its own wasDerivedFrom property
    # or form a cyclical chain of references via its wasDerivedFrom property
    # and those of other SBOL objects. For example, the reference chain
    # "A was derived from B and B was derived from A" is cyclical.
    # _wasDerivedFrom = None

    # An Activity which generated this ComponentDefinition,
    # eg., a design process like codon-optimization
    # or a construction process like Gibson Assembly
    # _wasGeneratedBy = None

    # The name property is OPTIONAL and has a data type of
    # String. This property is intended to be displayed to a human
    # when visualizing an Identified object. If an Identified object
    # lacks a name, then software tools SHOULD instead display the
    # object's displayId or identity. It is RECOMMENDED that software
    # tools give users the ability to switch perspectives between name
    # properties that are human-readable and displayId properties that
    # are less human-readable, but are more likely to be unique.
    # _name = None

    # The description property is OPTIONAL and has a data type of String.
    # This property is intended to contain a more thorough
    # text description of an Identified object.
    # _description = None

    def __init__(self, type_uri=SBOL_IDENTIFIED, uri=URIRef('example'),
                 version=VERSION_STRING):
        super().__init__(type_uri, uri)
        self.persistentIdentity = URIProperty(self, SBOL_PERSISTENT_IDENTITY,
                                              '0', '1', None, URIRef(uri))
        self.displayId = TextProperty(self, SBOL_DISPLAY_ID, '0', '1',
                                      [validation.sbol_rule_10204])
        self.version = VersionProperty(self, SBOL_VERSION, '0', '1', None, version)
        self.name = TextProperty(self, SBOL_NAME, '0', '1', None)
        self.description = TextProperty(self, SBOL_DESCRIPTION, '0', '1', None)
        if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
            self.displayId = uri
            self.persistentIdentity = URIRef(posixpath.join(getHomespace(), uri))
            if Config.getOption(ConfigOptions.SBOL_TYPED_URIS.value) is True:
                if self.version:
                    self.identity = URIRef(posixpath.join(getHomespace(),
                                                          self.getClassName(type_uri),
                                                          uri, str(self.version)))
                else:
                    self.identity = URIRef(posixpath.join(getHomespace(),
                                                          self.getClassName(type_uri),
                                                          uri))
            else:
                if self.version:
                    self.identity = URIRef(posixpath.join(getHomespace(),
                                                          uri, str(self.version)))
                else:
                    self.identity = URIRef(posixpath.join(getHomespace(), uri))
        elif hasHomespace():
            self.identity = URIRef(posixpath.join(getHomespace(), uri))
            self.persistentIdentity = URIRef(posixpath.join(getHomespace(),
                                                            uri))
        # Provo hooks
        self.wasDerivedFrom = URIProperty(self, SBOL_WAS_DERIVED_FROM,
                                          '0', '*', None)
        self.wasGeneratedBy = ReferencedObject(self, PROVO_WAS_GENERATED_BY,
                                               PROVO_WAS_GENERATED_BY, '0', '*', [])
        # self._identity.validate() # TODO

    def generate(self):
        raise NotImplementedError("Not yet implemented")

    def update_uri(self):
        """
        Recursively generates SBOL compliant ids for an object and all
        its owned objects, then checks to make sure that these ids are unique.
        :return: None
        """
        if self.parent is None:
            raise Exception('update_uri: Parent cannot be None')
        parent = self.parent
        if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
            # Form compliant URI for child object
            persistent_id = parent.properties[SBOL_PERSISTENT_IDENTITY][0]
            persistent_id = posixpath.join(persistent_id, self.displayId)
            if len(parent.properties[SBOL_VERSION]) > 0:
                version = parent.properties[SBOL_VERSION][0]
            else:
                version = VERSION_STRING
            obj_id = posixpath.join(persistent_id, version)
            # Reset SBOLCompliant properties
            self.identity = obj_id
            self.persistentIdentity = persistent_id
            # Check for uniqueness of URI in local object properties
            matches = parent.find_property_value(SBOL_IDENTIFIED, obj_id)
            if len(matches) > 0:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE,
                                "Cannot update SBOL-compliant URI. The URI " +
                                str(self.identity) + " is not unique")
            for rdf_type, store in self.owned_objects.items():
                if rdf_type not in self._hidden_properties:
                    for nested_obj in store:
                        nested_obj.update_uri()
        # Check for uniqueness of URI in Document
        if parent.doc:
            matches = parent.doc.find_property_value(SBOL_IDENTITY, self.identity)
            if len(matches) > 0:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE,
                                "Cannot update SBOL-compliant URI. "
                                "An object with URI " + str(self.identity) +
                                " is already in the Document")

    def copy(self, target_doc=None, target_namespace=None, version=None):

        new_obj = self.__class__()

        # This namespace map will be used later when copying namespaces over to
        # the new Document
        if self.doc:
            namespace_map = {ns: p for p, ns in self.doc._namespaces.items()}

        # Copy properties
        for property_uri, value_store in self.properties.items():
            new_obj.properties[property_uri] = value_store.copy()

            # Add a non-default namespace to the target document if not present
            # (This can happen when copying extension properties not in the
            # SBOL namespace, for example.)
            if self.doc and target_doc is not None:
                property_namespace = URIRef(parseNamespace(property_uri))
                if property_namespace in namespace_map.keys():
                    prefix = namespace_map[property_namespace]
                    target_doc.addNamespace(property_namespace, prefix)

        # If caller specified a target_namespace argument, then import objects into this
        # new namespace. This involves replacing the target_namespace in ReferenceObject
        # URIs with the current Homespace. Don't overwrite namespaces for the
        # wasDerivedFrom field, which points back to the original object
        if target_namespace:

            # Map the identity of self into the target namespace
            if hasattr(self, 'identity'):
                old_uri = self.identity
                new_uri = replace_namespace(old_uri, target_namespace, self.getTypeURI())
                new_obj.identity = new_uri

            if hasattr(self, 'persistentIdentity'):
                old_uri = self.persistentIdentity
                new_uri = replace_namespace(old_uri, target_namespace, self.getTypeURI())
                new_obj.persistentIdentity = new_uri

            # Map any references to other SBOL objects in the Document into the new
            # namespace
            if self.doc is not None:

                # Collect ReferencedObject attributes
                reference_properties = [p for p in new_obj.__dict__.values() if
                                        isinstance(p, ReferencedObject)]

                # These URIProperty attributes should be treated like ReferencedObject
                # attributes
                if '_built' in new_obj.__dict__.keys():
                    reference_properties.append(new_obj.__dict__['_built'])

                for reference_property in reference_properties:
                    values = new_obj.properties[reference_property._rdf_type]
                    new_values = []
                    for uri in values:
                        if target_namespace in uri:

                            referenced_object = self.doc.find(uri)
                            if referenced_object is None:
                                # This is a reference outside the document
                                # so retain the reference.
                                new_values.append(uri)
                                continue
                            new_uri = replace_namespace(uri, target_namespace,
                                                        referenced_object.getTypeURI())
                            new_values.append(new_uri)
                    new_obj.properties[reference_property._rdf_type] = new_values

        # Set the new object's version according to the user specified parameter. If
        # user didnt't provide a version, then set it automatically based on self's
        # version (if it has one).
        if version:
            new_obj.version = version
        elif self.version is not None:

            # If user is copying into the same Document and namespace, then assume the
            # user is trying to create a new version of the object. The version should
            # be automatically incremented to avoid a URI collision with the original
            # object.  However, if user is copying into a different Document, then copy
            # the original object's version without incrementing
            if self.doc and not target_doc and not target_namespace:
                new_obj.version = VersionProperty.increment_major(self.version)
            else:
                new_obj.version = self.version

        # Now set up the identity based on the persistentIdentity and maybe version
        # In the case of a Document there is no persistentIdentity so skip this block
        if new_obj.persistentIdentity:
            if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS) and new_obj.version:
                new_obj.identity = posixpath.join(new_obj.persistentIdentity,
                                                  new_obj.version)
            else:
                new_obj.identity = new_obj.persistentIdentity

        # Assign the new object to the target Document
        if target_doc:
            target_doc.add(new_obj)
        elif self.doc:
            self.doc.add(new_obj)

        # When an object is simply being cloned, the value of wasDerivedFrom should be
        # copied exactly as is from self. However, when copy is being used to generate
        # a new entity, the wasDerivedFrom should point back to self.
        if self.identity == new_obj.identity:
            new_obj.wasDerivedFrom = self.wasDerivedFrom
        else:
            new_obj.wasDerivedFrom = self.identity

        # Copy child objects recursively
        for property_uri, object_list in self.owned_objects.items():
            # Don't copy hidden properties
            if target_doc and property_uri in self._hidden_properties:
                continue
            for o in object_list:
                o_copy = o.copy(target_doc, target_namespace, version)
                new_obj.owned_objects[property_uri].append(o_copy)
                o_copy.parent = self
                # o_copy.update_uri()

        return new_obj


def parseNamespace(uri):
    '''
    Utility function for parsing the namespace from an RDF type -- note, this
    will work on some SBOL object URIs, but not universally.  It is primarily
    for use with RDF types.
    '''
    rlimit = uri.rfind('#') + 1
    if rlimit:
        return uri[:rlimit]
    rlimit = uri.rfind('/') + 1
    if rlimit:
        return uri[:rlimit]
    return ''


def replace_namespace(old_uri, target_namespace, rdf_type):
    """
    Utility function for mapping an SBOL object's identity into a new namespace. The
    rdf_type is used to map to and from sbol-typed namespaces.
    """

    # Work around an issue where the Document itself is being copied and
    # doesn't have its own URI, so old_uri is None. Return empty string
    # because the identity is not allowed to be None.
    if old_uri is None:
        return ''

    # If the value is an SBOL-typed URI, replace both the namespace and class name
    class_name = parseClassName(rdf_type)
    replacement_target = target_namespace + '/' + class_name

    # If not an sbol typed URI, then just replace the namespace
    if replacement_target not in old_uri:
        replacement_target = target_namespace

    if Config.getOption(ConfigOptions.SBOL_TYPED_URIS):
        # Map into a typed namespace
        replacement = getHomespace() + '/' + class_name
    else:
        # Map into a non-typed namespace
        replacement = getHomespace()

    new_uri = old_uri.replace(replacement_target, replacement)
    if type(old_uri) is URIRef:
        return URIRef(new_uri)
    return new_uri
