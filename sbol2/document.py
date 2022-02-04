import collections.abc
import logging
import os
import posixpath
import time
from typing import Any, Dict, Mapping, Union
import warnings

from deprecated import deprecated
from rdflib import URIRef

from . import SBOL2Serialize
from . import validation
from .attachment import Attachment
from .collection import Collection
from .combinatorialderivation import CombinatorialDerivation, VariableComponent
from .component import Component, FunctionalComponent
from .componentdefinition import ComponentDefinition
from .config import ConfigOptions
from .config import Config
from .config import parseClassName
from . import config
from .config import parsePropertyName
from .constants import *
from .dbtl import Analysis, Build, Design, SampleRoster, Test
from .experiment import Experiment, ExperimentalData
from .identified import Identified
from .implementation import Implementation
from .interaction import Interaction
from .location import Location, Range, Cut, GenericLocation
from .mapsto import MapsTo
from .measurement import Measurement
from .model import Model
from .module import Module
from .moduledefinition import ModuleDefinition
from .object import SBOLObject
from .participation import Participation
from .property import OwnedObject, URIProperty
from .provo import Plan, Activity, Agent, Usage, Association
from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode
from .sequence import Sequence
from .sequenceannotation import SequenceAnnotation
from .sequenceconstraint import SequenceConstraint
from .toplevel import TopLevel
from .uridict import URIDict
from .validator import do_validation  # local libSBOLj wrapper

import requests

Config.SBOL_DATA_MODEL_REGISTER = {
    URIRef(UNDEFINED): SBOLObject,
    URIRef(SBOL_IDENTIFIED): Identified,
    URIRef(SBOL_COMPONENT_DEFINITION): ComponentDefinition,
    URIRef(SBOL_SEQUENCE_ANNOTATION): SequenceAnnotation,
    URIRef(SBOL_SEQUENCE): Sequence,
    URIRef(SBOL_COMPONENT): Component,
    URIRef(SBOL_FUNCTIONAL_COMPONENT): FunctionalComponent,
    URIRef(SBOL_MODULE_DEFINITION): ModuleDefinition,
    URIRef(SBOL_MODULE): Module,
    URIRef(SBOL_INTERACTION): Interaction,
    URIRef(SBOL_PARTICIPATION): Participation,
    URIRef(SBOL_MODEL): Model,
    URIRef(SBOL_SEQUENCE_CONSTRAINT): SequenceConstraint,
    URIRef(SBOL_RANGE): Range,
    URIRef(SBOL_MAPS_TO): MapsTo,
    URIRef(SBOL_CUT): Cut,
    URIRef(SBOL_COLLECTION): Collection,
    URIRef(SBOL_LOCATION): Location,
    URIRef(SBOL_GENERIC_LOCATION): GenericLocation,
    URIRef(PROVO_PLAN): Plan,
    URIRef(PROVO_ACTIVITY): Activity,
    URIRef(PROVO_AGENT): Agent,
    URIRef(PROVO_USAGE): Usage,
    URIRef(PROVO_ASSOCIATION): Association,
    URIRef(SBOL_ATTACHMENT): Attachment,
    URIRef(SBOL_COMBINATORIAL_DERIVATION): CombinatorialDerivation,
    URIRef(SBOL_IMPLEMENTATION): Implementation,
    URIRef(SYSBIO_DESIGN): Design,
    URIRef(SYSBIO_ANALYSIS): Analysis,
    URIRef(SYSBIO_SAMPLE_ROSTER): SampleRoster,
    URIRef(SBOL_EXPERIMENT): Experiment,
    URIRef(SBOL_EXPERIMENTAL_DATA): ExperimentalData,
    URIRef(OM_MEASURE): Measurement,
    URIRef(SBOL_VARIABLE_COMPONENT): VariableComponent
}


class Document(Identified):
    """
    The Document is a container for all SBOL data objects.

    In a previous era, engineers might sit at a drafting board
    and draft a design by hand.
    The engineer's drafting sheet in LibSBOL is called a Document.
    The Document serves as a container,
    initially empty, for SBOL data objects.
    All file I/O operations are performed on the Document
    to populate it with SBOL objects representing design elements.
    """

    def __init__(self, filename=None):
        """
        Construct a document.

        :param filename: (optional) a file to initialize the Document.
        """
        super().__init__(SBOL_DOCUMENT, URIRef(""), VERSION_STRING)

        # A RDFLib representation of the triples.
        # Initialized when parsing a graph.
        # Updated when writing a graph.
        self.graph = rdflib.Graph()
        # The Document's register of objects
        self.objectCache = {}  # Needed?

        # The keys in SBOLObjects are URIRefs because our internal
        # representations use rdflib types.
        # self.SBOLObjects: Dict[rdflib.URIRef, SBOLObject] = {}
        self.SBOLObjects = URIDict()

        self._namespaces = {}
        self.resource_namespaces = set()
        self.designs = OwnedObject(self, SYSBIO_DESIGN, Design,
                                   '0', '*', [validation.libsbol_rule_11])
        self.builds = OwnedObject(self, SYSBIO_BUILD, Build,
                                  '0', '*', [validation.libsbol_rule_12])
        self.tests = OwnedObject(self, SYSBIO_TEST, Test,
                                 '0', '*', [validation.libsbol_rule_13])
        self.analyses = OwnedObject(self, SYSBIO_ANALYSIS, Analysis,
                                    '0', '*', [validation.libsbol_rule_14])
        self.componentDefinitions = OwnedObject(self,
                                                SBOL_COMPONENT_DEFINITION,
                                                ComponentDefinition,
                                                '0', '*', None)
        self.moduleDefinitions = OwnedObject(self,
                                             SBOL_MODULE_DEFINITION,
                                             ModuleDefinition,
                                             '0', '*', None)
        self.models = OwnedObject(self, SBOL_MODEL, Model,
                                  '0', '*', None)
        self.sequences = OwnedObject(self, SBOL_SEQUENCE, Sequence,
                                     '0', '*', None)
        self.collections = OwnedObject(self, SBOL_COLLECTION, Collection,
                                       '0', '*', None)
        self.activities = OwnedObject(self, PROVO_ACTIVITY, Activity,
                                      '0', '*', None)
        self.plans = OwnedObject(self, PROVO_PLAN, Plan,
                                 '0', '*', None)
        self.agents = OwnedObject(self, PROVO_AGENT, Agent,
                                  '0', '*', None)
        self.attachments = OwnedObject(self, SBOL_ATTACHMENT, Attachment,
                                       '0', '*', None)
        self.combinatorialderivations = OwnedObject(self,
                                                    SBOL_COMBINATORIAL_DERIVATION,
                                                    CombinatorialDerivation,
                                                    '0', '*', None)
        self.implementations = OwnedObject(self, SBOL_IMPLEMENTATION,
                                           Implementation,
                                           '0', '*', None)
        self.sampleRosters = OwnedObject(self, SYSBIO_SAMPLE_ROSTER,
                                         SampleRoster,
                                         '0', '*', [validation.libsbol_rule_16])
        self.experiments = OwnedObject(self, SBOL_EXPERIMENT, Experiment,
                                       '0', '*', None)
        self.experimentalData = OwnedObject(self, SBOL_EXPERIMENTAL_DATA,
                                            ExperimentalData,
                                            '0', '*', None)
        self.citations = URIProperty(self, PURL_URI + "bibliographicCitation",
                                     '0', '*', None)
        self.keywords = URIProperty(self, PURL_URI + "elements/1.1/subject",
                                    '0', '*', None)
        # I am my own document
        self.doc = self
        if filename is not None:
            self.read(filename)

    def compare(self, other):
        # Let the super class do the bulk of the comparison. Super
        # compares owned objects and properties.
        if not super().compare(other):
            return False
        if self._namespaces != other._namespaces:
            return False
        return True

    def addCitation(self, new_citation):
        val = self.citations
        val.append(new_citation)
        self.citations = val

    def removeCitation(self, index=0):
        val = self.citations
        del val[index]
        self.citations = val

    def addKeyword(self, new_keyword):
        val = self.keywords
        val.append(new_keyword)
        self.keywords = val

    def removeKeyword(self, index=0):
        val = self.keywords
        del val[index]
        self.keywords = val

    def add(self, sbol_obj):
        """
        Register an object in the Document.

        :param sbol_obj: The SBOL object(s) you want to serialize.
            Either a single object or a list of objects.
        :return: None
        """
        # Check for uniqueness of URI
        identity_uri = sbol_obj.identity
        if identity_uri in self.SBOLObjects:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE,
                            'Cannot add ' + sbol_obj.identity +
                            ' to Document. An object with this identity '
                            'is already contained in the Document')
        else:
            # If TopLevel add to Document.
            if sbol_obj.is_top_level():
                self.SBOLObjects[identity_uri] = sbol_obj
            type_uri = rdflib.URIRef(sbol_obj.getTypeURI())
            if type_uri in self.owned_objects:
                sbol_obj.parent = self  # Set back-pointer to parent object
                # Add the object to the Document's property store,
                # eg. componentDefinitions, moduleDefinitions, etc.
                self.owned_objects[type_uri].append(sbol_obj)
            sbol_obj.doc = self
            # Notify the object that it has been added
            sbol_obj._added_to_document(self)
            # Recurse into child objects and set their back-pointer to this Document
            for key, obj_store in sbol_obj.owned_objects.items():
                for child_obj in obj_store:
                    if child_obj.doc != self:
                        self.add(child_obj)

    def add_list(self, sbol_objs):
        for obj in sbol_objs:
            self.add(obj)

    def addNamespace(self, namespace, prefix):
        """Add a new namespace to the Document.

        :param namespace: The namespace, eg. http://sbols.org/v2#
        :param prefix: The namespace prefix, eg. sbol
        :return:
        """
        if namespace[-1] != '#' and namespace[-1] != '/':
            raise ValueError('Invalid namespace. Namespace must end with # or /')
        namespace = rdflib.term.URIRef(namespace)
        # Overwrite the prefix, if the namespace already has a conflicting one
        inv_namespace_map = {ns: p for p, ns in self._namespaces.items()}
        inv_namespace_map[namespace] = prefix
        self._namespaces = {p: ns for ns, p in inv_namespace_map.items()}

    def addComponentDefinition(self, sbol_obj):
        """
        Convenience method for adding a component definition.

        :param sbol_obj: component definition
        :return: None
        """
        if isinstance(sbol_obj, list):
            for obj in sbol_obj:
                self.add(obj)
        else:
            self.add(sbol_obj)

    def addModuleDefinition(self, sbol_obj):
        """
        Convenience method for adding a module definition.

        :param sbol_obj: module definition
        :return: None
        """
        if isinstance(sbol_obj, collections.abc.Iterable):
            for obj in sbol_obj:
                self.add(obj)
        else:
            self.add(sbol_obj)

    def addCollection(self, sbol_obj):
        """
        Convenience method for adding a collection.

        :param sbol_obj: a Collection
        :return: None
        """
        if isinstance(sbol_obj, collections.abc.Iterable):
            for obj in sbol_obj:
                self.add(obj)
        else:
            self.add(sbol_obj)

    def addSequence(self, sbol_obj):
        """
        Convenience method for adding a sequence.

        :param sbol_obj: sequence
        :return: None
        """
        self.add(sbol_obj)

    def addModel(self, sbol_obj):
        """
        Convenience method for adding a model.

        :param sbol_obj: model
        :return: None
        """
        self.add(sbol_obj)

    def addImplementation(self, implementation):
        """ Convenience method for adding an implementation.
        """
        if isinstance(implementation, collections.abc.Iterable):
            for impl in implementation:
                self.add(impl)
        else:
            self.add(implementation)

    def addAttachment(self, attachment):
        """Add an attachment to this document.
        """
        if isinstance(attachment, collections.abc.Iterable):
            for a in attachment:
                self.add(a)
        else:
            self.add(attachment)

    def create(self, uri):
        """
        Creates another SBOL object derived from TopLevel
        and adds it to the Document.
        NOTE: originally from ReferencedObject
        :param uri: In "open world" mode, this is a full URI
        and the same as the returned URI.
        If the default namespace for libSBOL has been configured,
        then this argument should simply be a local identifier.
        If SBOL-compliance is enabled,
        this argument should be the intended displayId of the new object.
        A full URI is automatically generated and returned.
        :return: The full URI of the created object
        """
        raise NotImplementedError("Not yet implemented")

    def get(self, uri):
        """ Finds the SBOL object with the given URI.

        :param uri: URI of the extension object
        :type uri: str
        :return: The matching SBOLObject
        :rtype: SBOLObject
        :raises: SBOLError if the given uri is not found
        """
        try:
            return self.SBOLObjects[uri]
        except KeyError:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_NOT_FOUND,
                            f'Object {uri} was not found')

    def getAll(self):
        """
        Retrieve a list of objects from the Document.

        :return: A list of objects from the Document.
        """
        raise NotImplementedError("Not yet implemented")

    def getComponentDefinition(self, uri):
        # NOTE: I couldn't find this in the original libSBOL source,
        # but they are heavily used in all the unit tests.
        return self.componentDefinitions.get(uri)

    def getModuleDefinition(self, uri):
        return self.moduleDefinitions.get(uri)

    def getSequence(self, uri):
        return self.sequences.get(uri)

    def getModel(self, uri):
        return self.models.get(uri)

    def getImplementation(self, uri):
        return self.implementations.get(uri)

    def getCollection(self, uri: str) -> Collection:
        return self.collections.get(uri)

    # File I/O #
    def write(self, filename):
        """
        Serialize all objects in this Document to an RDF/XML file.

        :param filename: The full name of the file you want to write
        (including file extension).
        :return: A string with the validation results,
        or empty string if validation is disabled.
        """
        self.doc_serialize_rdf2xml(filename)
        # Optionally validate
        result = 'Validation disabled. To enable use of validation, use'
        result += ' Config.setOption(ConfigOptions.VALIDATE, True)'
        if Config.getOption(ConfigOptions.VALIDATE):
            t_start = time.time()
            result = self.validate()
            if Config.getOption(ConfigOptions.VERBOSE):
                t_end = time.time()
                print(f'Validation request took {t_end - t_start} seconds')
        return result

    def read(self, filename):
        """
        Read an RDF/XML file and attach the SBOL objects to this Document.

        Existing contents of the Document will be wiped.
        :param filename: The full name of the file you want to read
        (including file extension).
        :return: None
        """
        self.clear()
        self.append(filename, overwrite=False)

    def readString(self, sbol_str):
        """Read an RDF/XML string and attach the SBOL objects to
        this Document.

        Existing contents of the Document will be wiped.

        :param sbol_str: A string formatted in SBOL.
        :return: None
        """
        self.clear()
        self.appendString(sbol_str, overwrite=False)

    def writeString(self):
        """
        Convert data objects in this Document into textual SBOL.

        :return: A string representation of the objects in this Document.
        """
        # Save any changes we've made to the graph.
        self.update_graph()
        # Write graph to string
        rdf = SBOL2Serialize.serialize_sboll2(self.graph).decode('utf-8')
        return rdf

    def append(self, filename, overwrite: bool = False):
        """
        Read an RDF/XML file and attach the SBOL objects to this Document.

        New objects will be added to the existing contents of the Document.
        :param filename: The full name of the file you want to read
        (including file extension).
        :param overwrite: Boolean indicating whether to overwrite existing objects
        :return: None
        """
        new_graph = rdflib.Graph()
        new_graph.parse(filename, format='application/rdf+xml')
        self._append_graph(new_graph, overwrite)

    def appendString(self, sbol_str: str, overwrite: bool = False):
        """
        Read an RDF/XML document from a string and attach the SBOL
        objects to this Document.

        New objects will be added to the existing contents of the Document.
        :param sbol_str: A string of RDF/XML
        :param overwrite: Boolean indicating whether to overwrite existing objects
        :return: None
        """
        # ------------------------------------------------------------
        # Load the new data into a graph
        new_graph = rdflib.Graph()
        new_graph.parse(data=sbol_str, format='application/rdf+xml')
        self._append_graph(new_graph, overwrite)

    def _append_graph(self, new_graph: rdflib.Graph, overwrite: bool):
        # Gather all the objects that will be overwritten, stopping
        # if the user says not to overwrite. If we clear as we go we lose
        # the ability to find objects within objects. So gather the list
        # here, and clear them as a second pass.
        objects_to_clear = []
        identities = (s for s, _, _ in
                      new_graph.triples((None, rdflib.RDF.type, None)))
        objects = (self.find(identity) for identity in identities)
        objects_to_clear = [obj for obj in objects if obj is not None]
        if overwrite is False and objects_to_clear:
            msg = objects_to_clear[0].identity
            count = len(objects_to_clear)
            if count > 1:
                msg += f' and {count - 1} others'
            msg += ' would require overwriting'
            raise SBOLError(SBOLErrorCode.DUPLICATE_URI_ERROR, msg)
        # Clear out the internal stores of the objects_to_clear so that
        # they will be overwritten. Keep the identity property because it
        # does not get restored by the graph parsing. Keep all the keys in
        # the internal stores so owned objects end up in the right place.
        for existing_object in objects_to_clear:
            if existing_object.identity not in self.SBOLObjects:
                self.SBOLObjects[existing_object.identity] = existing_object
            # Now clear the object. It will get reconstituted below by parse_all
            for k in existing_object.properties:
                # Clear out everything but the identity
                if k == SBOL_IDENTITY:
                    continue
                existing_object.properties[k] = []
            for k in existing_object.owned_objects:
                existing_object.owned_objects[k] = []
        # Make the new graph be the graph we parse
        self.graph = new_graph
        # Load the new graph into the existing document
        self.parse_all()

    def parse_all(self):
        # Parse namespaces
        self.logger.debug("*** Reading in namespaces (graph): ")
        for ns in self.graph.namespaces():
            self.logger.debug(ns)
            self._namespaces[ns[0]] = ns[1]
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("*** Internal namespaces data structure: ")
            for ns in self._namespaces:
                self.logger.debug(ns)
        # Instantiate all objects with an RDF type
        for s, _, o in self.graph.triples((None, rdflib.RDF.type, None)):
            self.parse_objects_inner(s, o)
        # Find the graph base uri.  This is the location of the sbol
        # file, and begins with the "file://" scheme.  Any URI in the
        # file without a scheme will appear relative to this URI, after
        # the file is parsed.  Therefore, if the any URI property value
        # begins with the graph base uri, the base part of the URI is removed.
        graphBaseURIStr = "file://" + os.getcwd()  # Not sure if this is correct...
        # Remove the filename from the path
        pos = graphBaseURIStr.rfind('/')
        if pos != -1:
            pos += 1
        rdf_type = rdflib.RDF.type
        for result_s, result_p, result_o in self.graph:
            # Look for properties
            if result_p != rdf_type:
                obj = result_o
                if isinstance(result_o, URIRef) and pos != -1:
                    if obj[:pos] == graphBaseURIStr:
                        # This was a URI without a scheme.  Remove URI base
                        obj = URIRef(obj[pos:])
                self.parse_properties_inner(result_s, result_p, obj)

        # Remove objects from SBOLObjects if they are not TopLevel AND
        # they have a parent object.
        #
        # Note: use a list of the keys so that we can modify the dict
        # while we iterate.
        for k in list(self.SBOLObjects.keys()):
            so = self.SBOLObjects[k]
            if isinstance(so, TopLevel):
                continue
            if so.parent:
                # Not TopLevel and already has parent, remove from
                # SBOLObjects
                del self.SBOLObjects[k]
                continue
            self.logger.debug('Orphan %r', so)

        # Handle the annotation objects
        self.parse_annotation_objects()
        # Dress document
        self.dress_document()

    def parse_objects_inner(self, subject, obj):
        # Construct the top-level object if we haven't already done so
        # and its type is something we know about.
        if subject not in self.SBOLObjects and obj in Config.SBOL_DATA_MODEL_REGISTER:
            # Call constructor for the appropriate SBOLObject
            new_obj = Config.SBOL_DATA_MODEL_REGISTER[obj]()
            if isinstance(new_obj, Identified):
                # Clear out the version. it will get set later
                new_obj.version = ''
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("New object type: " + str(type(new_obj)))
                self.logger.debug("New object attrs: " + str(vars(new_obj)))
            # Wipe default property values passed from default
            # constructor. New property values will be added as properties
            # are parsed from the input file
            for prop_name, values in new_obj.properties.items():
                values.clear()
            new_obj.identity = subject
            # Update document
            self.SBOLObjects[new_obj.identity] = new_obj
            new_obj.doc = self
            # For now, set the parent to the Document.
            # This may get overwritten later for child objects.
            new_obj.parent = self
            # If the new object is TopLevel,
            # add to the Document's property store
            if new_obj.is_top_level():
                if new_obj.rdf_type not in self.owned_objects:
                    self.owned_objects[new_obj.rdf_type] = []
                self.owned_objects[new_obj.rdf_type].append(new_obj)
        elif (subject not in self.SBOLObjects
              and obj not in Config.SBOL_DATA_MODEL_REGISTER):
            # Generic TopLevels
            new_obj = SBOLObject()
            new_obj.identity = subject
            new_obj.rdf_type = obj
            self.SBOLObjects[new_obj.identity] = new_obj
            new_obj.doc = self

    def parse_properties_inner(self, subject, predicate, obj):
        self.logger.debug('Adding (%r, %r, %r)', subject, predicate, obj)
        found = predicate.rfind('#')
        if found == -1:
            found = predicate.rfind('/')
        if found != -1:
            # Checks if the object's property already exists
            if subject in self.SBOLObjects:
                parent = self.SBOLObjects[subject]
                # Decide if this triple corresponds to a simple property,
                # a list property, an owned property or a referenced property
                if predicate in parent.properties:
                    # triple is a property
                    if obj not in parent.properties[predicate]:
                        parent.properties[predicate].append(obj)
                elif predicate in parent.owned_objects:
                    # triple is an owned object
                    owned_obj = self.SBOLObjects[obj]
                    if owned_obj is not None:
                        if owned_obj not in parent.owned_objects[predicate]:
                            parent.owned_objects[predicate].append(owned_obj)
                            owned_obj.parent = parent
                else:
                    # Extension data
                    parent.properties[predicate] = [obj]
            else:
                msg = 'Subject {} ({}) not found in my SBOLObjects'
                msg = msg.format(subject, type(subject))
                self.logger.debug(msg)

    def find_reference(self, uri):
        """Find objects that reference the given URI. Returns a list of
        objects. The list will be empty if no references were found.

        """
        references = []
        for obj in self.SBOLObjects.values():
            references.extend(obj.find_reference(uri))
        return references

    def parse_annotation_objects(self):
        """Parse leftover objects from reading and link them up where they
        belong. These are usually extension-type objects.

        """
        for uri, obj in self.SBOLObjects.items():
            self.logger.debug('Possible annotation object %s', obj.identity)
        annotation_objects = [obj for obj in self.SBOLObjects.values()
                              if not isinstance(obj, TopLevel)]
        for ao in annotation_objects:
            self.logger.debug('Annotation object: %s', ao.identity)
            if SBOL_PERSISTENT_IDENTITY in ao.properties:
                # Copy to a new TopLevel object
                tl = TopLevel(type_uri=ao.type, version=None)
                for k, v in ao.properties.items():
                    tl.properties[k] = v
                for k, v in ao.owned_objects.items():
                    tl.owned_objects[k] = v
                tl.doc = self
                tl_identity_uri = rdflib.URIRef(tl.identity)
                self.SBOLObjects[tl_identity_uri] = tl
            else:
                # Determine the RDF type of the member property that
                # contains this kind of annotation object
                ao_identity_uri = rdflib.URIRef(ao.identity)
                ns = config.parseNamespace(ao.type)
                self.logger.debug('anno ns = %r', ns)
                class_name = config.parseClassName(ao.type)
                self.logger.debug('anno class name = %r', class_name)
                # lowercase the first character
                property_name = class_name[0].lower() + class_name[1:]
                self.logger.debug('anno property name = %r', property_name)
                property_uri = rdflib.URIRef(posixpath.join(ns, property_name))
                self.logger.debug('anno property uri = %r', property_uri)
                matches = self.find_reference(ao_identity_uri)
                self.logger.debug('Found %d references', len(matches))
                matches = [m for m in matches if property_uri in m.properties]
                self.logger.debug('Found %d good references', len(matches))
                if len(matches) > 1:
                    msg = 'Invalid custom annotation object in SBOL document'
                    raise SBOLError(SBOLErrorCode.SBOL_ERROR_SERIALIZATION, msg)
                if len(matches) == 1:
                    match = matches[0]
                    if property_uri not in match.owned_objects:
                        match.owned_objects[property_uri] = []
                    match.owned_objects[property_uri].append(ao)
                    ao.parent = match
                    # Clean up the property
                    self.logger.debug('match[%r] = %r', property_uri,
                                      match.properties[property_uri])
                    self.logger.debug('ao.identity = %r', ao.identity)
                    match.properties[property_uri].remove(ao_identity_uri)
                    if len(match.properties[property_uri]) == 0:
                        # Remove the empty property list
                        del match.properties[property_uri]
                    # Remove this annotation object from the list of
                    # SBOLObjects
                    ao_identity_uri = rdflib.URIRef(ao.identity)
                    del self.SBOLObjects[ao_identity_uri]

    def infer_resource_namespaces(self):
        for obj in self.SBOLObjects.values():
            if not isinstance(obj, Identified):
                continue
            if not (obj.persistentIdentity and obj.displayId and obj.version):
                continue
            # if object identity ends with compliant suffix, extract the
            # start as a namespace
            uri = obj.identity
            compliant_suffix = posixpath.join(posixpath.sep, obj.displayId,
                                              obj.version)
            if uri.endswith(compliant_suffix):
                self.resource_namespaces.add(uri[0:-len(compliant_suffix)])
                continue
            typed_suffix = posixpath.join(posixpath.sep, parseClassName(obj.rdf_type),
                                          obj.displayId, obj.version)
            if uri.endswith(typed_suffix):
                self.resource_namespaces.add(uri[0:-len(typed_suffix)])

    def dress_document(self):
        self.infer_resource_namespaces()
        # There is a lot more that is done in libSBOL Document::dress_document()
        # TODO: do more of that here

    def convert_ntriples_encoding_to_ascii(self, s):
        s.replace("\\\"", "\"")
        s.replace("\\\\", "\\")
        return s

    def request_comparison(self, diff_file):
        """
        Perform comparison on Documents using the online validation tool.

        This is for cross-validation of SBOL documents with libSBOLj.
        Document comparison can also be performed using the built-in compare method.
        :param diff_file:
        :return: The comparison results
        """
        raise NotImplementedError("Not yet implemented")

    def clear(self, clear_graph=True):
        """
        Delete all properties and objects in the Document.

        :return: None
        """
        # Properties to keep, which don't make sense to clear
        keepers = [SBOL_VERSION]
        self.SBOLObjects.clear()
        for name, value in self.properties.items():
            if name in keepers:
                # Do not erase properties on the keepers list
                continue
            value.clear()
        for object_store in self.owned_objects.values():
            object_store.clear()
        self._namespaces.clear()
        self.resource_namespaces.clear()
        if clear_graph:
            self.graph = rdflib.Graph()  # create a new graph

    def query_repository(self, command):
        """

        :param command:
        :return: str
        """
        # TODO better docstring
        raise NotImplementedError("Not yet implemented")

    def search_metadata(self, role, type, name, collection):
        """

        :param role:
        :param type:
        :param name:
        :param collection:
        :return: str
        """
        # TODO better docstring
        raise NotImplementedError("Not yet implemented")

    def doc_serialize_rdf2xml(self, outfile):
        """
        Serialize RDF XML.
        :param outfile: output file
        :return: None
        """
        self.update_graph()
        rdf = SBOL2Serialize.serialize_sboll2(self.graph).decode('utf-8')
        self.logger.debug("RDF: " + rdf)
        self.logger.debug("TYPE: " + str(type(rdf)))
        with open(outfile, 'w') as out:
            out.write(rdf)
            out.flush()

    def update_graph(self):
        """
        Update the RDF triples representation of data.
        :return:
        """
        self.graph = rdflib.Graph()
        for prefix, ns in self._namespaces.items():
            self.graph.bind(prefix, ns)
        # ASSUMPTION: Document does not have properties. Is this a valid assumption?
        for obj in self.SBOLObjects.values():
            obj.build_graph(self.graph)
        if self.logger.isEnabledFor(logging.DEBUG):
            for s, p, o in self.graph:
                self.logger.debug('Graph contains: %r', (s, p, o))

    def validate(self):
        """
        Run validation on this Document via the validation tool (locally or online, depending on configuration)

        :return: A string containing a message with the validation results
        :rtype: str
        """
        response = validate(self, config.options)
        if response['valid']:
            result = "Valid."
        else:
            result = "Invalid."
        errors = ' '.join(response['errors'])
        if errors:
            result = ' '.join([result, errors])
        return result

    def size(self):
        """
        Get the total number of objects in the Document,
        including SBOL core object and custom annotation objects.

        :return: The total number of objects in the Document.
        """
        return len(self.SBOLObjects)

    def __len__(self):
        """
        Get the total number of objects in the Document,
        including SBOL core object and custom annotation objects.

        (Returns the same thing as size())

        :return: The total number of objects in the Document.
        """
        return self.size()

    def __bool__(self):
        # Ignore list semantics for boolean conversion.
        # A document is True if it exists.
        return True

    def __str__(self):
        """
        Produce a string representation of the Document.

        :return: A string representation of the Document.
        """
        return self.summary()

    # def __iter__(self):
    #     self.current_obj = 0
    #     self.owned_objects_list = []
    #     for objlist in self.owned_objects.values():
    #         for obj in objlist:
    #             self.owned_objects_list.append(obj)
    #     return self
    #

    def __iter__(self):
        self.current_obj = 0
        self.owned_objects_list = []
        for obj in self.SBOLObjects.values():
            self.owned_objects_list.append(obj)
        return self

    def __next__(self):
        if self.current_obj > len(self.owned_objects_list)-1:
            raise StopIteration
        else:
            ret = self.owned_objects_list[self.current_obj]
            self.current_obj += 1
            return ret

    def cacheObjectsDocument(self):
        # TODO docstring
        raise NotImplementedError("Not yet implemented")

    def referenceNamespace(self, uri):
        """Replaces the namespace with a reference
        and removes the default namespace, shortening the URI.
        :param uri:
        :return: str
        """
        if self._default_namespace is not None and \
                len(self._default_namespace) > 0:
            if self._default_namespace in uri:
                uri.replace(self._default_namespace, '')
                return uri
        for abbrev, ns in self._namespaces.items():
            if ns in uri:
                # Assume only one namespace per URI
                uri.replace(ns, abbrev)
                return uri

    def summary(self):
        """
        Produce a string representation of the Document.

        :return: A string representation of the Document.
        """
        summary = ''
        col_size = 30
        total_core_objects = 0
        for rdf_type, obj_store in self.owned_objects.items():
            property_name = parsePropertyName(rdf_type)
            obj_count = len(obj_store)
            total_core_objects += obj_count
            summary += property_name
            summary += '.' * (col_size-len(property_name))
            summary += str(obj_count) + '\n'
        summary += 'Annotation Objects'
        summary += '.' * (col_size-18)
        summary += str(self.size() - total_core_objects) + '\n'
        summary += '---\n'
        summary += 'Total: '
        summary += '.' * (col_size-5)
        summary += str(self.size()) + '\n'
        return summary

    # TODO Port iterator, which loops over top-level items of Document

    def find(self, uri):
        """
        Search recursively for an SBOLObject in this Document
        that matches the uri.

        :param uri: The identity of the object to search for.
        :return: A pointer to the SBOLObject,
        or NULL if an object with this identity doesn't exist.
        """
        for obj in self.SBOLObjects.values():
            match = obj.find(uri)
            if match is not None:
                return match
        return None

    def getTypeURI(self):
        return URIRef(SBOL_DOCUMENT)

    def getTopLevel(self, uri):
        # Ensure it's a URI Ref
        uri = rdflib.URIRef(uri)
        if uri not in self.SBOLObjects:
            msg = 'Top level object {} is not in document'
            msg = msg.format(uri)
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_NOT_FOUND, msg)
        sbol_obj = self.SBOLObjects[uri]
        # Verify object is top level
        if sbol_obj.is_top_level():
            return sbol_obj
        # Not top level, raise error
        msg = '{} is not a top level object'
        msg = msg.format(uri)
        raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)

    def copy(self, target_namespace=None, target_doc=None, version=None):
        # This enables the user to use the pattern doc2 = doc.copy() to clone a Document.
        # SWIG pySBOL assumes the user does NOT want to increment the Document's version
        # when creating a clone. (Whether or not these are the right semantics, that's
        # how it is implemented.) By passing an explicit version parameter to super's
        # copy method, we short-circuit its default behavior to auto-increment version.
        if version is None:
            version = self.version
        return super().copy(target_doc, target_namespace, version)

    def exportToFormat(self, language: str, output_path: str):
        # Copy the global config options. Shallow copy is ok because values
        # are either bool or str.
        options = config.options.copy()
        options[ConfigOptions.LANGUAGE.value] = language
        # We always want the return file
        options[ConfigOptions.RETURN_FILE.value] = True
        response = validate(self, options)

        if response['valid'] is not True:
            # The validator would not translate this document
            msg = 'Invalid Document'
            if response['errors'][0]:
                # Append the error messages to the message using
                # newlines to separate the lines.
                errors = '\n'.join(response['errors'])
                msg = f'{msg}\n{errors}'
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)
        # write the result to the desired output path
        with open(output_path, 'w') as fp:
            fp.write(response['result'])

    def convert(self, language, output_path):
        warnings.warn('Document.convert is now Document.exportToFormat',
                      DeprecationWarning)
        self.exportToFormat(language, output_path)

    def importFromFormat(self, input_path: str, overwrite=False):
        """Import the specified file into this document.
        """
        # The C++ version of this function takes a language argument
        # and does not use it. There is no need for a language
        # argument based on the validator API.
        # Copy the global config options. Shallow copy is ok because values
        # are either bool or str.
        options = config.options.copy()
        # We want an SBOL2 file back
        options[ConfigOptions.LANGUAGE.value] = 'SBOL2'
        options[ConfigOptions.URI_PREFIX.value] = Config.getHomespace()

        json_request = _make_validation_request(options)
        # We always want the return file.
        json_request[ConfigOptions.RETURN_FILE.value] = True

        # get the input file data to send
        with open(input_path, 'r') as infile:
            contents = infile.read()
        json_request['main_file'] = contents

        validate_online = Config.getOption(ConfigOptions.VALIDATE_ONLINE)
        if not validate_online:
            response = do_validation(json_request)
        else:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'charsets': 'utf-8'
            }

            validator_url = options[ConfigOptions.VALIDATOR_URL.value]

            # Send the request to the online validation tool
            response = requests.post(validator_url,
                                     json=json_request,
                                     headers=headers)
            if response:
                response = response.json()
            else:
                msg = 'Validation failure. HTTP post request failed with code {}: {}'
                msg = msg.format(response.status_code, response.content)
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST, msg)

        if response['valid']:
            self.appendString(response['result'], overwrite)
        else:
            msg = ' '.join(response['errors'])
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)

    @deprecated(reason="Use Document.get() instead")
    def getExtensionObject(self, uri: str) -> SBOLObject:
        """*Deprecated.* Use Document.get instead.

        :param uri: URI of the extension object
        :type uri: str
        :return: The matching SBOLObject
        :rtype: SBOLObject
        :raises: SBOLError if the given uri is not found
        """
        return self.get(uri)

    @deprecated(reason="Use Document.add() instead")
    def addExtensionObject(self, obj: SBOLObject) -> None:
        """
        *Deprecated.* Use Document.add instead.

        :param obj: An SBOLObject to add to this document
        :type obj: SBOLObject
        :return: None
        """
        # Just do an add
        self.add(obj)


def _make_validation_request(options: Mapping[str, Union[bool, str]]):
    config_options = [
        config.ConfigOptions.CHECK_BEST_PRACTICES.value,
        config.ConfigOptions.CHECK_COMPLETENESS.value,
        config.ConfigOptions.CHECK_URI_COMPLIANCE.value,
        config.ConfigOptions.DIFF_FILE_NAME.value,
        config.ConfigOptions.FAIL_ON_FIRST_ERROR.value,
        config.ConfigOptions.INSERT_TYPE.value,
        config.ConfigOptions.LANGUAGE.value,
        config.ConfigOptions.MAIN_FILE_NAME.value,
        config.ConfigOptions.PROVIDE_DETAILED_STACK_TRACE.value,
        config.ConfigOptions.SUBSET_URI.value,
        config.ConfigOptions.TEST_EQUALITY.value,
        config.ConfigOptions.URI_PREFIX.value,
        config.ConfigOptions.VERSION.value
    ]
    request_options = {}
    for key in config_options:
        request_options[key] = options[key]
    return dict(options=request_options)


def validate(doc: Document, options: Mapping[str, Any]):
    """
    :rtype: Dict[str, Any]
    """
    return_file_key = config.ConfigOptions.RETURN_FILE.value
    validator_key = config.ConfigOptions.VALIDATOR_URL.value
    validate_online = Config.getOption(ConfigOptions.VALIDATE_ONLINE)
    json_request = _make_validation_request(options)
    # We always want the return file
    json_request[return_file_key] = options[return_file_key]
    json_request['main_file'] = doc.writeString()

    if not validate_online:
        result = do_validation(json_request)
        return result
    else:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'charsets': 'utf-8'
        }

        validator_url = options[validator_key]

        # Send the request to the online validation tool
        response = requests.post(validator_url,
                                 json=json_request,
                                 headers=headers)
        if response:
            return response.json()
        else:
            msg = 'Validation failure. HTTP post request failed with code {}: {}'
            msg = msg.format(response.status_code, response.content)
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST, msg)


igem_assembly_scars = '''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:dcterms="http://purl.org/dc/terms/"
xmlns:gbconv="http://sbols.org/genBankConversion#"
xmlns:genbank="http://www.ncbi.nlm.nih.gov/genbank#"
xmlns:igem="http://wiki.synbiohub.org/wiki/Terms/igem#"
xmlns:ncbi="http://www.ncbi.nlm.nih.gov#"
xmlns:obo="http://purl.obolibrary.org/obo/"
xmlns:om="http://www.ontology-of-units-of-measure.org/resource/om-2/"
xmlns:prov="http://www.w3.org/ns/prov#"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
xmlns:sbh="http://wiki.synbiohub.org/wiki/Terms/synbiohub#"
xmlns:sbol="http://sbols.org/v2#"
xmlns:sybio="http://www.sybio.ncl.ac.uk#"
xmlns:synbiohub="http://synbiohub.org#"
xmlns:xsd="http://www.w3.org/2001/XMLSchema#dateTime/">
<sbol:ComponentDefinition rdf:about="https://synbiohub.org/public/igem/BBa_G0000/1">
<dc:creator>Reshma Shetty</dc:creator>
<dcterms:created>2007-07-22T11:00:00Z</dcterms:created>
<dcterms:description>SpeI/XbaI scar for RBS-CDS junctions</dcterms:description>
<dcterms:modified>2015-08-31T04:07:27Z</dcterms:modified>
<dcterms:title>scar</dcterms:title>
<sbol:displayId>BBa_G0000</sbol:displayId>
<sbol:persistentIdentity rdf:resource="https://synbiohub.org/public/igem/BBa_G0000"/>
<sbol:role rdf:resource="http://identifiers.org/so/SO:0000110"/>
<sbol:role rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#partType/DNA"/>
<sbol:sequence
        rdf:resource="https://synbiohub.org/public/igem/BBa_G0000_sequence/1"/>
<sbol:type rdf:resource="http://www.biopax.org/release/biopax-level3.owl#DnaRegion"/>
<sbol:version>1</sbol:version>
<igem:discontinued>false</igem:discontinued>
<igem:dominant>true</igem:dominant>
<igem:experience
        rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#experience/None"/>
<igem:group_u_list>_41_</igem:group_u_list>
<igem:m_user_id>0</igem:m_user_id>
<igem:owner_id>126</igem:owner_id>
<igem:owning_group_id>162</igem:owning_group_id>
<igem:sampleStatus>Not in stock</igem:sampleStatus>
<igem:status
        rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#status/Unavailable"/>
<sbh:bookmark>false</sbh:bookmark>
<sbh:mutableDescription>
    This is the sequence of the SpeI/XbaI scar for RBS-CDS junctions in
    BioBricks standard assembly.
</sbh:mutableDescription>
<sbh:mutableNotes>
    This is a shorter scar to ensure proper spacing between the RBS and CDS.
</sbh:mutableNotes>
<sbh:mutableProvenance>SpeI/XbaI scar</sbh:mutableProvenance>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/james"/>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/myers"/>
<sbh:star>false</sbh:star>
<sbh:topLevel rdf:resource="https://synbiohub.org/public/igem/BBa_G0000/1"/>
<prov:wasDerivedFrom rdf:resource="http://parts.igem.org/Part:BBa_G0000"/>
<prov:wasGeneratedBy rdf:resource="https://synbiohub.org/public/igem/igem2sbol/1"/>
</sbol:ComponentDefinition>
<sbol:Sequence rdf:about="https://synbiohub.org/public/igem/BBa_G0000_sequence/1">
<sbol:displayId>BBa_G0000_sequence</sbol:displayId>
<sbol:elements>tactag</sbol:elements>
<sbol:encoding rdf:resource="http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html"/>
<sbol:persistentIdentity
        rdf:resource="https://synbiohub.org/public/igem/BBa_G0000_sequence"/>
<sbol:version>1</sbol:version>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/james"/>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/myers"/>
<sbh:topLevel rdf:resource="https://synbiohub.org/public/igem/BBa_G0000_sequence/1"/>
<prov:wasDerivedFrom rdf:resource="http://parts.igem.org/Part:BBa_G0000"/>
<prov:wasGeneratedBy rdf:resource="https://synbiohub.org/public/igem/igem2sbol/1"/>
</sbol:Sequence>
<sbol:ComponentDefinition rdf:about="https://synbiohub.org/public/igem/BBa_G0002/1">
<dc:creator>Reshma Shetty</dc:creator>
<dcterms:created>2007-02-26T12:00:00Z</dcterms:created>
<dcterms:description>SpeI/XbaI mixed site</dcterms:description>
<dcterms:modified>2015-08-31T04:07:27Z</dcterms:modified>
<dcterms:title>SX scar</dcterms:title>
<sbol:displayId>BBa_G0002</sbol:displayId>
<sbol:persistentIdentity rdf:resource="https://synbiohub.org/public/igem/BBa_G0002"/>
<sbol:role rdf:resource="http://identifiers.org/so/SO:0000110"/>
<sbol:role rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#partType/DNA"/>
<sbol:sequence rdf:resource="https://synbiohub.org/public/igem/BBa_G0002_sequence/1"/>
<sbol:type rdf:resource="http://www.biopax.org/release/biopax-level3.owl#DnaRegion"/>
<sbol:version>1</sbol:version>
<igem:discontinued>false</igem:discontinued>
<igem:dominant>true</igem:dominant>
<igem:experience
        rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#experience/None"/>
<igem:group_u_list>_41_</igem:group_u_list>
<igem:m_user_id>0</igem:m_user_id>
<igem:owner_id>126</igem:owner_id>
<igem:owning_group_id>70</igem:owning_group_id>
<igem:sampleStatus>Not in stock</igem:sampleStatus>
<igem:status
        rdf:resource="http://wiki.synbiohub.org/wiki/Terms/igem#status/Unavailable"/>
<sbh:bookmark>false</sbh:bookmark>
<sbh:mutableDescription>
    XbaI/SpeI mixed site.  Simply used to aid in entry of parts into the registry.
</sbh:mutableDescription>
<sbh:mutableNotes>None.</sbh:mutableNotes>
<sbh:mutableProvenance>XbaI and SpeI sites</sbh:mutableProvenance>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/james"/>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/myers"/>
<sbh:star>false</sbh:star>
<sbh:topLevel rdf:resource="https://synbiohub.org/public/igem/BBa_G0002/1"/>
<prov:wasDerivedFrom rdf:resource="http://parts.igem.org/Part:BBa_G0002"/>
<prov:wasGeneratedBy rdf:resource="https://synbiohub.org/public/igem/igem2sbol/1"/>
</sbol:ComponentDefinition>
<sbol:Sequence rdf:about="https://synbiohub.org/public/igem/BBa_G0002_sequence/1">
<sbol:displayId>BBa_G0002_sequence</sbol:displayId>
<sbol:elements>tactagag</sbol:elements>
<sbol:encoding rdf:resource="http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html"/>
<sbol:persistentIdentity
        rdf:resource="https://synbiohub.org/public/igem/BBa_G0002_sequence"/>
<sbol:version>1</sbol:version>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/james"/>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/myers"/>
<sbh:topLevel rdf:resource="https://synbiohub.org/public/igem/BBa_G0002_sequence/1"/>
<prov:wasDerivedFrom rdf:resource="http://parts.igem.org/Part:BBa_G0002"/>
<prov:wasGeneratedBy rdf:resource="https://synbiohub.org/public/igem/igem2sbol/1"/>
</sbol:Sequence>
<prov:Activity rdf:about="https://synbiohub.org/public/igem/igem2sbol/1">
<dc:creator>Chris J. Myers</dc:creator>
<dc:creator>James Alastair McLaughlin</dc:creator>
<dcterms:description>Conversion of the iGEM parts registry to SBOL2.1
</dcterms:description>
<dcterms:title>iGEM to SBOL conversion</dcterms:title>
<sbol:displayId>igem2sbol</sbol:displayId>
<sbol:persistentIdentity rdf:resource="https://synbiohub.org/public/igem/igem2sbol"/>
<sbol:version>1</sbol:version>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/james"/>
<sbh:ownedBy rdf:resource="https://synbiohub.org/user/myers"/>
<sbh:topLevel rdf:resource="https://synbiohub.org/public/igem/igem2sbol/1"/>
<prov:endedAtTime>2017-03-06T15:00:00.000Z</prov:endedAtTime>
</prov:Activity>
</rdf:RDF>'''


def IGEM_STANDARD_ASSEMBLY(parts_list):
    if not all(type(part) is ComponentDefinition for part in parts_list):
        raise TypeError()
    doc = parts_list[0].doc
    G0000_uri = 'https://synbiohub.org/public/igem/BBa_G0000/1'
    G0000_seq_uri = 'https://synbiohub.org/public/igem/BBa_G0000_sequence/1'
    G0002_uri = 'https://synbiohub.org/public/igem/BBa_G0002/1'
    G0002_seq_uri = 'https://synbiohub.org/public/igem/BBa_G0002_sequence/1'
    if not (G0000_uri in doc.componentDefinitions and
            G0002_uri in doc.componentDefinitions and
            G0000_seq_uri in doc.sequences and G0002_seq_uri in doc.sequences):
        doc.appendString(igem_assembly_scars, overwrite=True)

    G0000 = doc.componentDefinitions[G0000_uri]
    G0002 = doc.componentDefinitions[G0002_uri]
    new_parts_list = []
    for upstream, downstream in zip(parts_list[:-1], parts_list[1:]):
        new_parts_list.append(upstream)
        if SO_RBS in upstream.roles and SO_CDS in downstream.roles:
            new_parts_list.append(G0000)
        else:
            new_parts_list.append(G0002)
    new_parts_list.append(downstream)
    return new_parts_list
