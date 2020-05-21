from rdflib import URIRef

from .component import Component
from .config import Config
from .constants import *
from .toplevel import TopLevel
from . import validation
from .property import OwnedObject, ReferencedObject, URIProperty
from .sbolerror import SBOLError, SBOLErrorCode
from .sequence import Sequence
from .sequenceannotation import SequenceAnnotation
from .sequenceconstraint import SequenceConstraint


class ComponentDefinition(TopLevel):
    """
    The ComponentDefinition class represents the structural entities
    of a biological design.

    The primary usage of this class is to represent structural entities
    with designed sequences, such as DNA, RNA, and proteins,
    but it can also be used to represent
    any other entity that is part of a design,
    such as small molecules, proteins, and complexes.
    """

    # The types property is a REQUIRED set of URIs that specifies
    # the category of biochemical or physical entity
    # (for example DNA, protein, or small molecule)
    # that a ComponentDefinition object abstracts
    # for the purpose of engineering design.
    # The types property of every ComponentDefinition
    # MUST contain one or more URIs that MUST identify terms
    # from appropriate ontologies, such as the BioPAX ontology
    # or the ontology of Chemical Entities of Biological Interest.
    # See the table below for examples.
    # | Type              | URI for BioPAX Term                                           | LibSBOL symbol        |  # noqa
    # | :---------------- | :------------------------------------------------------------ | :-------------------- |  # noqa
    # | DNA               | http://www.biopax.org/release/biopax-level3.owl#DnaRegion     | BIOPAX_DNA            |  # noqa
    # | RNA               | http://www.biopax.org/release/biopax-level3.owl#RnaRegion     | BIOPAX_RNA            |  # noqa
    # | Protein           | http://www.biopax.org/release/biopax-level3.owl#Protein       | BIOPAX_PROTEIN        |  # noqa
    # | Small Molecule    | http://www.biopax.org/release/biopax-level3.owl#SmallMolecule | BIOPAX_SMALL_MOLECULE |  # noqa
    # | Complex           | http://www.biopax.org/release/biopax-level3.owl#Complex       | BIOPAX_COMPLEX        |  # noqa
    _types = None  # URIProperty

    # The roles property is an OPTIONAL set of URIs
    # that clarifies the potential function of the entity represented
    # by a ComponentDefinition in a biochemical or physical context.
    # The roles property of a ComponentDefinition MAY
    # contain one or more URIs that MUST identify terms
    # from ontologies that are consistent with the types property
    # of the ComponentDefinition.
    # For example, the roles property of a DNA or RNA ComponentDefinition
    # could contain URIs identifying terms from the Sequence Ontology (SO).
    # See the table below for common examples.
    # | Role              | URI for Sequence Ontology Term            | LibSBOL symbol    |  # noqa
    # | :---------------- | :---------------------------------------- | :---------------- |  # noqa
    # | Miscellaneous     | http://identifiers.org/so/SO:0000001      | SO_MISC           |  # noqa
    # | Promoter          | http://identifiers.org/so/SO:0000167      | SO_PROMOTER       |  # noqa
    # | RBS               | http://identifiers.org/so/SO:0000139      | SO_RBS            |  # noqa
    # | CDS               | http://identifiers.org/so/SO:0000316      | SO_CDS            |  # noqa
    # | Terminator        | http://identifiers.org/so/SO:0000141      | SO_TERMINATOR     |  # noqa
    # | Gene              | http://identifiers.org/so/SO:0000704      |                   |  # noqa
    # | Operator          | http://identifiers.org/so/SO:0000057      |                   |  # noqa
    # | Engineered Gene   | http://identifiers.org/so/SO:0000280      |                   |  # noqa
    # | mRNA              | http://identifiers.org/so/SO:0000234      |                   |  # noqa
    # | Effector          | http://identifiers.org/chebi/CHEBI:35224  |                   |  # noqa
    _roles = None  # URIProperty

    # The components property is OPTIONAL and MAY
    # specify a set of Component objects that are contained
    # by the ComponentDefinition. The components properties
    # of ComponentDefinition objects can be used
    # to construct a hierarchy of Component and ComponentDefinition objects.
    # If a ComponentDefinition in such a hierarchy refers to
    # one or more Sequence objects, and there exist
    # ComponentDefinition objects lower in the hierarchy
    # that refer to Sequence objects with the same encoding,
    # then the elements properties of these Sequence objects
    # SHOULD be consistent with each other, such that well-defined mappings
    # exist from the "lower level" elements
    # to the "higher level" elements. This mapping is also subject
    # to any restrictions on the positions of the Component objects
    # in the hierarchy that are imposed by the SequenceAnnotation
    # or SequenceConstraint objects contained
    # by the ComponentDefinition objects in the hierarchy.
    # The set of relations between Component and ComponentDefinition objects
    # is strictly acyclic.
    components = None  # OwnedObject<Component>

    sequences = None  # ReferencedObject

    sequence = None  # OwnedObject<Sequence>

    sequenceAnnotations = None  # OwnedObject<SequenceAnnotation>

    sequenceConstraints = None  # OwnedObject<SequenceConstraint>

    def __init__(self, uri=URIRef("example"),
                 component_type=URIRef(BIOPAX_DNA),
                 version=VERSION_STRING,
                 rdf_type=SBOL_COMPONENT_DEFINITION):
        """Construct a ComponentDefinition.

        :param uri: A full URI including a scheme, namespace, and identifier.
        If SBOLCompliance configuration is enabled, then this argument
        is simply the displayId for the new object
        and a full URI will automatically be constructed.
        :param component_type: A BioPAX ontology term
        that indicates whether the ComponentDefinition
        is DNA, RNA, protein, or some other molecule type.
        :param version: An arbitrary version string.
        If SBOLCompliance is enabled, this should be a Maven version string
        of the form "major.minor.patch".
        :param rdf_type: The RDF type for an extension class
        derived from this one
        """
        super().__init__(rdf_type, uri, version)
        self._types = URIProperty(self, SBOL_TYPES,
                                  '1', '*', None, component_type)
        self._roles = URIProperty(self, SBOL_ROLES,
                                  '0', '*', None)
        self.sequence = OwnedObject(self, SBOL_SEQUENCE,
                                    Sequence,
                                    '0', '1', [libsbol_rule_20])
        self.sequences = ReferencedObject(self, SBOL_SEQUENCE_PROPERTY,
                                          SBOL_SEQUENCE, '0', '*',
                                          [validation.libsbol_rule_21])
        self.sequenceAnnotations = OwnedObject(self, SBOL_SEQUENCE_ANNOTATIONS,
                                               SequenceAnnotation,
                                               '0', '*', None)
        self.components = OwnedObject(self, SBOL_COMPONENTS, Component,
                                      '0', '*', None)
        self.sequenceConstraints = OwnedObject(self, SBOL_SEQUENCE_CONSTRAINTS,
                                               SequenceConstraint,
                                               '0', '*', None)
        self._hidden_properties = [SBOL_SEQUENCE]

    @property
    def types(self):
        return self._types.value

    @types.setter
    def types(self, new_types):
        # perform validation prior to setting the value of the types property
        self._types.set(new_types)

    def addType(self, new_types):
        self._types.add(new_types)

    def removeType(self, index=0):
        self._types.remove(index)

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

    def assemble(self, component_list, assembly_method=None, doc=None):
        """Assembles ComponentDefinitions into an abstraction hierarchy.

        The resulting data structure is a partial design,
        still lacking a primary structure or explicit sequence.
        To form a primary structure out of the ComponentDefinitions,
        call linearize after calling assemble.
        To fully realize the target sequence, use Sequence::assemble().
        :param component_list: Either a list of URIs
        for the constituent ComponentDefinitions or a list of subcomponents.
        A list of displayIds is also acceptable if using SBOL-compliant URIs.
        :param assembly_method: An optional argument
        such as IGEM_STANDARD_ASSEMBLY that affects how components
        are composed and the final target sequence.
        :param doc: The Document to which the assembled ComponentDefinitions
        will be added. If not set, then you must add this ComponentDefinition
        to a Document before calling this method.
        :return: None
        """

        # Due to the recursive nature of this routine, it is hard to completely
        # validate that all the necessary preconditions for successful execution are met
        # prior to execution. That means if a call fails, it may result in a modified
        # and incomplete data structure that will be difficult to fix when the user is
        # working interactively in the interpreter
        if not Config.getOption('sbol_compliant_uris'):
            raise EnvironmentError('Assemble method requires SBOL-compliance enabled')

        # Validate doc
        if not self.doc and not doc:
            raise ValueError('Missing doc argument. If the ComponentDefinition does '
                             'not belong to a Document, a target Document must be '
                             'specified using the doc keyword argument.')
        if doc and self.doc != doc:
            raise ValueError('Invalid doc argument. Do not use the doc keyword '
                             'argument if the ComponentDefinition already belongs '
                             'to a Document')

        # Validate component_list
        doc = doc if doc else self.doc
        if isinstance(component_list, list) and all(isinstance(c, ComponentDefinition)
                                                    for c in component_list):
            for cdef in component_list:
                if cdef.doc and cdef.doc.this != doc.this:
                    raise ValueError('Invalid component_list specified. Assembly '
                                     'subcomponents must belong to the same Document '
                                     'as self.')
        elif isinstance(component_list, list) and all(isinstance(c, str)
                                                      for c in component_list):
            component_identities = component_list[:]
            component_list = []
            for c_id in component_identities:
                if c_id not in doc.componentDefinitions:
                    raise ValueError('Invalid component_list specified. '
                                     'ComponentDefinition <%s> not found.' % c_id)
                cdef = doc.componentDefinitions[c_id]
                component_list.append(cdef)
        else:
            raise TypeError('Invalid component_list specified. Please provide a list '
                            'of ComponentDefinitions or, alternatively, a list of '
                            'ComponentDefinition displayIds')

        if not self.doc:
            doc.addComponentDefinition(self)
        for cdef in component_list:
            if not cdef.doc:
                self.doc.addComponentDefinition(cdef)

        if assembly_method:
            component_list = assembly_method(component_list)
            if not all(type(c) is ComponentDefinition for c in component_list):
                raise TypeError('Invalid callback specified for assembly_method. The '
                                'callback must return a list of ComponentDefinitions')

        # Instantiate a Component for each ComponentDefinition in the list
        instance_list = []
        for cdef in component_list:

            # Generate URI of new Component.  Check if an object with that URI is
            # already instantiated.
            instance_count = 0
            component_id = self.persistentIdentity + "/" + cdef.displayId + "_" \
                + str(instance_count) + "/" + self.version
            while self.find(component_id):
                # Find the last instance assigned
                instance_count += 1
                component_id = self.persistentIdentity + "/" + cdef.displayId + "_" \
                    + str(instance_count) + "/" + self.version

            c = self.components.create(cdef.displayId + "_" + str(instance_count))
            c.definition = cdef.identity
            instance_list.append(c)
        return component_list

    def assemblePrimaryStructure(self, primary_structure, assembly_method=None,
                                 doc=None):
        """Assembles ComponentDefinition into a linear primary structure.

        The resulting data structure is a partial design,
        still lacking an explicit sequence.
        To fully realize the target sequence, use Sequence::assemble().
        :param primary_structure: Either a list of URIs
        for the constituent ComponentDefinitions
        or a list of subcomponents.
        A list of displayIds is also acceptable if using SBOL-compliant URIs.
        :param assembly_standard: An optional argument
        such as IGEM_STANDARD_ASSEMBLY that affects
        how components are composed and the final target sequence.
        :param doc: The Document to which the assembled ComponentDefinitions
        will be added. If not set, then you must add this ComponentDefinition
        to a Document before calling this method.
        :return: None
        """
        primary_structure = self.assemble(primary_structure, assembly_method, doc)

        # If user specifies a list of IDs rather than ComponentDefinitions, convert to
        # list of ComponentDefinitions (Some parameter validation is done by the
        # preceding call to ComponentDefinition.assemble)
        doc = doc if doc else self.doc
        if all(isinstance(c, str) for c in primary_structure):
            component_identities = primary_structure[:]
            primary_structure = []
            for c_id in component_identities:
                cdef = doc.componentDefinitions[c_id]
                primary_structure.append(cdef)

        self.types += [SO_LINEAR]

        component_map = {}
        for c in self.components:
            if c.definition not in component_map:
                component_map[c.definition] = [c]
            else:
                component_map[c.definition].append(c)
        primary_structure_components = []
        for cd in primary_structure:
            primary_structure_components.append(component_map[cd.identity].pop())

        # Iterate pairwise through the primary_structure, and place SequenceConstraints
        # between adjacent ComponentDefinitions.
        if len(self.sequenceConstraints):
            self.sequenceConstraints.clear()
        for upstream, downstream in zip(primary_structure_components[:-1],
                                        primary_structure_components[1:]):
            instance_count = 0
            constraint_id = 'constraint_%d' % instance_count
            while constraint_id in self.sequenceConstraints:
                instance_count += 1
                constraint_id = 'constraint_%d' % instance_count
            sc = self.sequenceConstraints.create(constraint_id)
            sc.subject = upstream
            sc.object = downstream
            sc.restriction = SBOL_RESTRICTION_PRECEDES

    def compile(self, assembly_method=None):
        """Compiles an abstraction hierarchy of ComponentDefinitions
        into a nucleotide sequence.

        If no Sequence object is associated with this ComponentDefinition,
        one will be automatically instantiated
        :return: A string representing the nucleotide sequence
        for this ComponentDefinition.
        """
        if not self.doc:
            raise ValueError('Cannot compile <%s>. The ComponentDefinition must belong '
                             'to a Document in order to compile.' % self.identity)

        if self.sequence is None:
            if Config.getOption('sbol_compliant_uris'):
                display_id = self.displayId
                if not Config.getOption('sbol_typed_uris'):
                    display_id += '_seq'
                self.sequence = Sequence(display_id)
            else:
                self.sequence = Sequence(display_id + '_seq')

        return self.sequence.compile(assembly_method=assembly_method)

    def updateSequence(self, composite_sequence=""):
        """Assemble a parent ComponentDefinition's Sequence
        from its subcomponent Sequences.

        :param composite_sequence: A recursive parameter, use default value.
        :return: The assembled parent sequence.
        """
        raise NotImplementedError("Not yet implemented")

    def getInSequentialOrder(self):
        """Get the primary sequence of a design in terms of its sequentially ordered
        Components.

        :return: A list of Components.
        """
        return self.getPrimaryStructureComponents()

    def hasUpstreamComponent(self, component):
        """Checks if the specified Component has a Component upstream
        in linear arrangement on the DNA strand.

        Checks that the appropriate SequenceConstraint exists.
        :param current_component: A Component in this ComponentDefinition.
        :return: True if found, False if not
        """
        if len(self.sequenceConstraints) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'Cannot determine upstream Component. '
                            'Self has no SequenceConstraints')
        else:
            for sc in self.sequenceConstraints:
                if sc.object == component.identity and \
                      sc.restriction == SBOL_RESTRICTION_PRECEDES:
                    return True
            return False

    def getUpstreamComponent(self, component):
        """Get the upstream component.

        :param component: A Component in this ComponentDefinition.
        :return: The upstream component.
        """
        if len(self.sequenceConstraints) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'Cannot get upstream Component. Self '
                            'has no SequenceConstraints')
        else:
            upstream_component_id = None
            for sc in self.sequenceConstraints:
                if sc.object == component.identity and \
                      sc.restriction == SBOL_RESTRICTION_PRECEDES:
                    upstream_component = self.components[sc.subject]
                    return upstream_component
        raise SBOLError(SBOL_ERROR_END_OF_LIST, 'This component has no upstream '
                        'component. Use hasUpstreamComponent to catch this error')

    def hasDownstreamComponent(self, component):
        """Checks if the specified Component has a Component downstream
        in linear arrangement on the DNA strand.

        Checks that the appropriate SequenceConstraint exists.
        :param current_component: A Component in this ComponentDefinition.
        :return: True if found, False if not.
        """
        if len(self.sequenceConstraints) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'Cannot determine upstream Component. '
                            'Self has no SequenceConstraints')
        else:
            for sc in self.sequenceConstraints:
                if sc.subject == component.identity and \
                      sc.restriction == SBOL_RESTRICTION_PRECEDES:
                    return True
            return False

    def getDownstreamComponent(self, component):
        """Get the downstream component.

        :param current_component: A Component in this ComponentDefinition.
        :return: The downstream component.
        """
        if len(self.sequenceConstraints) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'Cannot get downstream Component. '
                            'Self has no SequenceConstraints')
        else:
            upstream_component_id = None
            for sc in self.sequenceConstraints:
                if sc.subject == component.identity and \
                      sc.restriction == SBOL_RESTRICTION_PRECEDES:
                    upstream_component = self.components[sc.object]
                    return upstream_component
        raise SBOLError(SBOL_ERROR_END_OF_LIST, 'This component has no downstream '
                        'component. Use hasDownstreamComponent to catch this error')

    def getFirstComponent(self):
        """Gets the first Component in a linear sequence.

        :return: The first component in sequential order.
        """

        # A Component's sequential position in the primary structure does not
        # necessarily correspond with its index in the components list (Rather
        # this must be determined by reasoning over SequenceConstraints)
        if len(self.components) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'This ComponentDefinition has no '
                            'components')

        arbitrary_component = self.components[0]
        next_component = arbitrary_component
        while self.hasUpstreamComponent(next_component):
            next_component = self.getUpstreamComponent(next_component)
        return next_component

    def getLastComponent(self):
        """Gets the last Component in a linear sequence.

        :return: The last component in sequential order.
        """

        # A Component's sequential position in the primary structure does not
        # necessarily correspond with its index in the components list (Rather
        # this must be determined by reasoning over SequenceConstraints)
        if len(self.components) < 1:
            raise SBOLError(SBOL_ERROR_NOT_FOUND, 'This ComponentDefinition has no '
                            'components')

        arbitrary_component = self.components[0]
        next_component = arbitrary_component
        while self.hasDownstreamComponent(next_component):
            next_component = self.getDownstreamComponent(next_component)
        return next_component

    def applyToComponentHierarchy(self, callback=None, user_data=None):
        """Perform an operation on every Component in a structurally-linked
        hierarchy of Components by applying a callback function.
        If no callback is specified, the default behavior is to return
        a list of each Component in the hierarchy.

        :param callback: The callback function to apply.
        :param user_data: Arbitrary user data which can be passed
        in and out of the callback as an argument.
        :return: A list of all Components in the hierarchy.
        """
        raise NotImplementedError("Not yet implemented")

    def getPrimaryStructureComponents(self):
        """Get the primary sequence of a design in terms of its sequentially ordered
        Components.

        :return: A list of Components.
        """
        subcomponents = []
        if len(self.components) == 1:
            subcomponents.append(self.components[0])
        else:
            # Check if this is a complete primary structure
            # (note this isn't a perfect test)
            if len(self.sequenceConstraints) != (len(self.components) - 1):
                raise ValueError('ComponentDefinition <%s> does not appear to describe'
                                 'a complete primary structure. It appears to be '
                                 'missing SequenceConstraints.' % self.identity)

            c_first = self.getFirstComponent()
            subcomponents.append(c_first)
            c_next = c_first
            while self.hasDownstreamComponent(c_next):
                c_next = self.getDownstreamComponent(c_next)
                subcomponents.append(c_next)
        return subcomponents

    def getPrimaryStructure(self):
        """Get the primary sequence of a design in terms of its sequentially ordered
        ComponentDefinitions.

        :return: A list of ComponentDefinitions.
        """
        if self.doc is None:
            raise SBOLError(SBOL_ERROR_MISSING_DOCUMENT, 'Cannot get primary structure.'
                            'Self must belong to a Document.')
        component_ids = [c.definition for c in self.getPrimaryStructureComponents()]
        return [self.doc.getComponentDefinition(c) for c in component_ids]

    def insertDownstream(self, target, component_to_insert):
        """Insert a Component downstream of another in a primary sequence,
        shifting any adjacent Components downstream as well.

        :param target: The target Component will be upstream
        of the insert Component after this operation.
        :param component_to_insert: The insert Component
        is inserted downstream of the target Component.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def insertUpstream(self, target, component_to_insert):
        """Insert a Component upstream of another in a primary sequence,
        shifting any adjacent Components upstream as well.


        :param target: The target Component will be downstream
        of the insert Component after this operation.
        :param component_to_insert: The insert Component is inserted upstream
        of the target Component.
        :return:
        """
        raise NotImplementedError("Not yet implemented")

    def addUpstreamFlank(self, target, elements):
        """A useful method when building up SBOL representations
        of natural DNA sequences.

        For example, it is often necessary to specify components
        that are assumed to have no meaningful role in the design,
        but are nevertheless important to fill in regions of sequence.
        This method autoconstructs a ComponentDefinition and Sequence object
        to create an arbitrary flanking sequence around design Components.
        The new ComponentDefinition will have Sequence Ontology type
        of flanking_region or SO:0000239.
        :param target: The new flanking sequence will be placed upstream
        of the target.
        :param elements: The primary sequence elements will be assigned
        to the autoconstructed Sequence object.
        The encoding is inferred.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def addDownstreamFlank(self, target, elements):
        """A useful method when building up SBOL representations
        of natural DNA sequences.

        For example, it is often necessary to specify components
        that are assumed to have no meaningful role
        in the design, but are nevertheless important
        to fill in regions of sequence. This method autoconstructs
        a ComponentDefinition and Sequence object to create an arbitrary
        flanking sequence around design Components.
        The new ComponentDefinition will have Sequence Ontology type
        of flanking_sequence.
        :param target: The new flanking sequence will be placed downstream
        of the target.
        :param elements: The primary sequence elements will be assigned
        to the autoconstructed Sequence object.
        The encoding is inferred.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def isRegular(self, msg=None):
        """Use this diagnose an irregular design.

        Recursively checks if this ComponentDefinition
        defines a SequenceAnnotation and Range for every Sequence.
        Regularity is more stringent than completeness.
        A design must be complete to be regular.
        :param msg: An optional message for diagnosing the irregularity,
        if any is found.
        :return: True if the abstraction hierarchy is regular,
        False otherwise.
        """
        raise NotImplementedError("Not yet implemented")

    def isComplete(self, msg=None):
        """Use this diagnose an incomplete design.

        Recursively checks if this ComponentDefinition defines
        a SequenceAnnotation and Range for every Sequence.
        Completeness does not guarantee regularity.
        :param msg: An optional message for diagnosing the irregularity,
        if any is found.
        :return: True if the abstraction hierarchy is complete, False otherwise.
        """
        raise NotImplementedError("Not yet implemented")

    def disassemble(self, range_start=1):
        """Instantiates a Component for every SequenceAnnotation

         When converting from a flat GenBank file to a flat SBOL file,
         the result is a ComponentDefinition with SequenceAnnotations.
         This method will convert the flat SBOL file
         into hierarchical SBOL.

        :param range_start:
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def linearize(self, components=None):
        """
        TODO document

        :param components: An optional list of component definitions or URIs.
        If None, an empty list of ComponentDefinitions is assumed.
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def build(self):
        """
        TODO document

        :return: A ComponentDefinition.
        """
        raise NotImplementedError("Not yet implemented")

    def participate(self, species):
        """A convenience method that assigns a component to participate
        in a biochemical reaction.

        Behind the scenes, it auto-constructs a FunctionalComponent
        for this ComponentDefinition and assigns it to a Participation.

        :param species: A Participation object
        (ie. participant species in a biochemical Interaction).
        :return: None
        """
        raise NotImplementedError("Not yet implemented")

    def getTypeURI(self):
        return SBOL_COMPONENT_DEFINITION


def libsbol_rule_20(sbol_obj, arg):
    """Synchronizes ComponentDefinition.sequence with ComponentDefinition.sequences.
    """
    if not isinstance(sbol_obj, ComponentDefinition):
        msg = 'Expected {}, got {}'
        msg = msg.format(ComponentDefinition.__name__, type(sbol_obj).__name__)
        raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
    if arg is None:
        # Clearing out sequence. What should we do with sequences?
        # Should we clear sequences?
        return
    if not isinstance(arg, Sequence):
        msg = 'Expected {}, got {}'
        msg = msg.format(Sequence.__name__, type(arg).__name__)
        raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
    if arg.identity not in sbol_obj.sequences:
        sbol_obj.sequences = [arg.identity]
