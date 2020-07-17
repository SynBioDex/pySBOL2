from deprecated import deprecated
from rdflib import URIRef

from .constants import *
from .property import URIProperty, TextProperty
from .toplevel import TopLevel
from .config import Config, ConfigOptions
from .sbolerror import SBOLError, SBOLErrorCode
from .location import Range


class Sequence(TopLevel):
    """
    The primary structure (eg, nucleotide or amino acid sequence)
    of a ComponentDefinition object.
    """

    def __init__(self, uri=URIRef("example"), elements="",
                 encoding=SBOL_ENCODING_IUPAC,
                 version=VERSION_STRING, type_uri=SBOL_SEQUENCE):
        """Construct a Sequence.

        :param uri: A full URI including a scheme, namespace, and identifier.
        If SBOLCompliance configuration is enabled, then this argument is
        simply the displayId for the new object and a full URI will
        automatically be constructed.
        :param elements: A string representation of the primary structure
        of DNA, RNA, protein, or a SMILES string for small molecules.
        :param encoding: A URI that describes the representation format
        used for the elements property. Set to SBOL_ENCODING_IUPAC by default
        :param version: An arbitrary version string. If SBOLCompliance is
        enabled, this should be a Maven version string.
        :param type_uri: The RDF type for an extension class derived
        from this one.
        """
        super().__init__(type_uri, uri, version)

        # The elements property is a REQUIRED String of characters that represents
        # the constituents of a biological or chemical molecule. For example,
        # these characters could represent the nucleotide bases
        # of a molecule of DNA, the amino acid residues of a protein,
        # or the atoms and chemical bonds of a small molecule.
        self.elements = TextProperty(self, SBOL_ELEMENTS,
                                     '1', '1', [], elements)
        self.encoding = URIProperty(self, SBOL_ENCODING,
                                    '1', '1', [], encoding)

    # The encoding property is REQUIRED and has a data type of URI.
    # This property MUST indicate how the elements property of a Sequence
    # MUST be formed and interpreted. For example, the elements property
    # of a Sequence with an IUPAC DNA encoding property MUST contain characters
    # that represent nucleotide bases, such as a, t, c, and g.
    # The elements property of a Sequence with a Simplified Molecular-Input
    # Line-Entry System (SMILES) encoding, on the other hand,
    # MUST contain characters that represent atoms and chemical bonds,
    # such as C, N, O, and =.
    #
    # It is RECOMMENDED that the encoding property contains a URI
    # from the table below. The terms in the table are organized
    # by the type of ComponentDefinition that typically refer to a Sequence
    # with such an encoding.
    # When the encoding of a Sequence is well described by one of the URIs
    # in the table, it MUST contain that URI.
    # | ComponentDefinition type  | Encoding       | libSBOL Symbol              | URI                                              |
    # | :------------------------ | :--------------| :-------------------------- | :----------------------------------------------- |
    # | DNA, RNA                  | IUPAC DNA, RNA | SBOL_ENCODING_IUPAC         | http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html |
    # | Protein                   | IUPAC Protein  | SBOL_ENCODING_IUPAC_PROTEIN | http://www.chem.qmul.ac.uk/iupac/AminoAcid/      |
    # | Small Molecule            | SMILES         | SBOL_ENCODING_SMILES        | http://www.opensmiles.org/opensmiles.html        |

    def __len__(self):
        """

        :return: The length of the primary sequence in the elements property.
        """
        return len(self.elements)

    def __bool__(self):
        # Ignore list semantics for boolean conversion.
        # A sequence is True if it exists.
        return True

    @deprecated(reason='Use len(sequence) instead')
    def length(self):
        """

        :return: The length of the primary sequence in the elements property.
        """
        return len(self)

    def synthesize(self, clone_id):
        """

        :param clone_id: A URI for the build, or displayId if working in
        SBOLCompliant mode.
        :return:
        """
        raise NotImplementedError("Not yet implemented")

    def compile(self, composite_sequence='', assembly_method=None):
        if not self.doc:
            raise ValueError('Cannot compile Sequence <%s>. The Sequence must belong to '
                             'a Document in order to compile.' % self.identity)

        # Search for the parent ComponentDefinition to which this Sequence belongs
        parent_cdef = None
        for cd in self.doc.componentDefinitions:
            if cd.sequence and cd.sequence.identity == self.identity:
                parent_cdef = cd
                break

        if not parent_cdef:
            raise ValueError('Cannot compile Sequence <%s>. The Sequence must be '
                             'associated with a ComponentDefinition in order to compile.'
                             % self.identity)

        if len(parent_cdef.components) == 0:
            if parent_cdef.sequence.elements:
                return parent_cdef.sequence.elements
            else:
                return ''  # Maybe this should raise an Exception ?

        elif len(parent_cdef.components) > 0:
            # Recurse into subcomponents and assemble their sequence
            composite_sequence_initial_size = len(composite_sequence)

            subcomponents = parent_cdef.getPrimaryStructureComponents()
            for c in subcomponents:
                cdef = self.doc.getComponentDefinition(c.definition)
                if not cdef.sequence:
                    if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS):
                        seq = self.doc.sequences.create(cdef.displayId)
                        # cdef.sequence = seq
                        cdef.sequences = seq.identity
                    else:
                        seq = self.doc.sequences.create(cdef.identity + '_seq')
                        # cdef.sequence = seq
                        cdef.sequences = seq.identity
                seq = cdef.sequence

                # Check for regularity -- only one SequenceAnnotation per Component is
                # allowed
                sequence_annotations = \
                    parent_cdef.find_property_value(SBOL_COMPONENT_PROPERTY, c.identity)

                if len(sequence_annotations) > 1:
                    raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                    'Cannot compile Sequence. Component <%s> is '
                                    'irregular. More than one SequenceAnnotation is '
                                    'associated with this Component' % c.identity)

                # Auto-construct a SequenceAnnotation for this Component if one doesn't
                # already exist
                if len(sequence_annotations) == 0:
                    sa_instance = 0
                    if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS):
                        sa_id = cdef.displayId
                    else:
                        sa_id = cdef.identity
                    sa_id += '_annotation'
                    sa_uri = '%s/%s_%d/%s' % (parent_cdef.persistentIdentity, sa_id,
                                              sa_instance, cdef.version)
                    while sa_uri in parent_cdef.sequenceAnnotations:
                        sa_instance += 1
                        sa_uri = '%s/%s_%d/%s' % (parent_cdef.persistentIdentity, sa_id,
                                                  sa_instance, cdef.version)
                    sa = parent_cdef.sequenceAnnotations.create('%s_%d' % (sa_id,
                                                                sa_instance))
                    sa.component = c
                    sequence_annotations.append(sa)

                sa = sequence_annotations[0]

                # Check for regularity--only one Range per SequenceAnnotation is allowed
                ranges = []

                # Look for an existing Range that can be re-used
                for loc in sa.locations:
                    if type(loc) is Range:
                        ranges.append(loc)
                else:
                    # Auto-construct a Range
                    if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS):
                        range_id = sa.displayId
                    else:
                        range_id = sa.identity
                    r = sa.locations.createRange(range_id + '_range')
                    ranges.append(r)
                if len(ranges) > 1:
                    raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                    'Cannot compile Sequence <%s> because '
                                    'SequenceAnnotation <%s> has more than one Range.'
                                    % (self.identity, sa.identity))

                r = ranges[0]
                r.start = len(composite_sequence) + 1
                subsequence = seq.compile(composite_sequence)  # Recursive call
                if assembly_method:
                    subsequence = assembly_method(subsequence)
                    if not type(subsequence) is str:
                        raise TypeError('Invalid callback specified for assembly_method.'
                                        ' The callback must return a string.')

                # If sourceLocation is specified, don't use the entire sequence for the
                # subcomponent
                if len(c.sourceLocations) == 1:
                    source_loc = c.sourceLocations.getRange()
                    subsequence = subsequence[(source_loc.start - 1):source_loc.end]
                composite_sequence = composite_sequence + subsequence
                r.end = len(composite_sequence)

            composite_sequence_current_size = composite_sequence_initial_size \
                + len(composite_sequence)
            subsequence = composite_sequence[composite_sequence_initial_size:
                                             composite_sequence_current_size]
            self.elements = subsequence
            return subsequence
