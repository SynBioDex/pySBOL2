from enum import Enum
from typing import Any
import warnings

from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode
from rdflib import URIRef


class FileFormats(Enum):
    JSON = 'json'
    NTRIPLES = 'ntriples'
    RDFXML = 'rdfxml'


class ConfigOptions(Enum):
    HOMESPACE = 'homespace'
    SBOL_COMPLIANT_URIS = 'sbol_compliant_uris'
    SBOL_TYPED_URIS = 'sbol_typed_uris'
    SERIALIZATION_FORMAT = 'serialization_format'
    VALIDATE = 'validate'
    VALIDATE_ONLINE = 'validate_online'
    VALIDATOR_URL = 'validator_url'
    JAVA_LOCATION = 'java_location'
    LANGUAGE = 'language'
    TEST_EQUALITY = 'test_equality'
    CHECK_URI_COMPLIANCE = 'check_uri_compliance'
    CHECK_COMPLETENESS = 'check_completeness'
    CHECK_BEST_PRACTICES = 'check_best_practices'
    FAIL_ON_FIRST_ERROR = 'fail_on_first_error'
    PROVIDE_DETAILED_STACK_TRACE = 'provide_detailed_stack_trace'
    URI_PREFIX = 'uri_prefix'
    SUBSET_URI = 'subset_uri'
    VERSION = 'version'
    INSERT_TYPE = 'insert_type'
    MAIN_FILE_NAME = 'main_file_name'
    DIFF_FILE_NAME = 'diff_file_name'
    RETURN_FILE = 'return_file'
    VERBOSE = 'verbose'


options = {
    ConfigOptions.HOMESPACE.value: 'http://examples.org',
    ConfigOptions.SBOL_COMPLIANT_URIS.value: True,
    ConfigOptions.SBOL_TYPED_URIS.value: True,
    ConfigOptions.SERIALIZATION_FORMAT.value: 'sbol',
    ConfigOptions.VALIDATE.value: True,
    ConfigOptions.VALIDATE_ONLINE.value: True,
    ConfigOptions.VALIDATOR_URL.value: 'https://validator.sbolstandard.org/validate/',
    ConfigOptions.JAVA_LOCATION.value: '/usr/bin/java',
    ConfigOptions.LANGUAGE.value: 'SBOL2',
    ConfigOptions.TEST_EQUALITY.value: False,
    ConfigOptions.CHECK_URI_COMPLIANCE.value: False,
    ConfigOptions.CHECK_COMPLETENESS.value: False,
    ConfigOptions.CHECK_BEST_PRACTICES.value: False,
    ConfigOptions.FAIL_ON_FIRST_ERROR.value: False,
    ConfigOptions.PROVIDE_DETAILED_STACK_TRACE.value: False,
    ConfigOptions.URI_PREFIX.value: '',
    ConfigOptions.SUBSET_URI.value: '',
    ConfigOptions.VERSION.value: '',
    ConfigOptions.INSERT_TYPE.value: False,
    ConfigOptions.MAIN_FILE_NAME.value: 'main file',
    ConfigOptions.DIFF_FILE_NAME.value: 'comparison file',
    ConfigOptions.RETURN_FILE.value: False,
    ConfigOptions.VERBOSE.value: False
}


valid_options = {
    ConfigOptions.SBOL_COMPLIANT_URIS.value: {True, False},
    ConfigOptions.SBOL_TYPED_URIS.value: {True, False},
    ConfigOptions.SERIALIZATION_FORMAT.value: {'sbol', 'rdfxml',
                                               'json', 'ntriples'},
    ConfigOptions.VALIDATE.value: {True, False},
    ConfigOptions.VALIDATE_ONLINE.value: {True, False},
    ConfigOptions.LANGUAGE.value: {'SBOL2', 'FASTA', 'GenBank'},
    ConfigOptions.TEST_EQUALITY.value: {True, False},
    ConfigOptions.CHECK_URI_COMPLIANCE.value: {True, False},
    ConfigOptions.CHECK_COMPLETENESS.value: {True, False},
    ConfigOptions.CHECK_BEST_PRACTICES.value: {True, False},
    ConfigOptions.FAIL_ON_FIRST_ERROR.value: {True, False},
    ConfigOptions.PROVIDE_DETAILED_STACK_TRACE.value: {True, False},
    ConfigOptions.INSERT_TYPE.value: {True, False},
    ConfigOptions.RETURN_FILE.value: {True, False},
    ConfigOptions.VERBOSE.value: {True, False}
}


extension_namespaces = {}
# The authoritative namespace for the Document.
# Setting the home namespace is like signing a piece of paper.
home = None
# Flag indicating whether an object's type is included in SBOL-compliant URIs.
SBOLCompliantTypes = 1
catch_exceptions = 0
file_format = 'rdfxml'


class Config:
    """A class which contains global configuration variables
    for the libSBOL environment.

    Configuration variables are accessed
    through the setOption and getOption methods.
    """

    # Dictionary which holds builder functions for SBOL objects. The key is the
    # RDFtype of the object which is parsed from the SBOL file. The dictionary is
    # populated with SBOL core classes in document.py.  The dictionary also supports
    # extension classes with RDFtypes not part of the core specification
    SBOL_DATA_MODEL_REGISTER = {}

    @staticmethod
    def register_extension_class(builder, type_uri):
        """Register an extension class and its namespace, so custom data
        can be embedded into and read from SBOL files.

        :param builder: A no-argument constructor
        :param type_uri: An RDF type URI for the extension class
        """
        Config.SBOL_DATA_MODEL_REGISTER[URIRef(type_uri)] = builder

    @staticmethod
    def setHomespace(ns):
        """Setting the Homespace has several advantages.
        It simplifies object creation and retrieval from Documents.
        In addition, it serves as a way for a user
        to claim ownership of new objects.
        Generally users will want to specify a Homespace
        that corresponds to their organization's web domain.
        :param ns: The namespace to use as the Homespace
        :return: None
        """
        options[ConfigOptions.HOMESPACE.value] = ns

    @staticmethod
    def getHomespace():
        """

        :return: The Homespace (a string representing the default namespace).
        """
        return options[ConfigOptions.HOMESPACE.value]

    @staticmethod
    def hasHomespace():
        """

        :return: True if Homespace is set, False otherwise.
        """
        homespace = ConfigOptions.HOMESPACE.value
        return (homespace in options and
                options[homespace] is not None and
                options[homespace] != "")

    @staticmethod
    def setFileFormat(_file_format):
        """

        :param _file_format: The file format to use.
        :return: None
        """
        # must declare that we're assigning to a global variable
        global file_format
        if _file_format == FileFormats.JSON.value:
            file_format = FileFormats.JSON.value
        elif _file_format == FileFormats.NTRIPLES.value:
            file_format = FileFormats.NTRIPLES.value
        else:
            file_format = FileFormats.RDFXML.value

    @staticmethod
    def getFileFormat():
        """

        :return: The file format.
        """
        return file_format

    @staticmethod
    def setOption(option, val):
        """
        Configure options for libSBOL. Access online validation and conversion.

        | Option                       | Description                                                              | Values          |   # noqa
        | :--------------------------- | :----------------------------------------------------------------------- | :-------------- |
        | homespace                    | Enable validation and conversion requests through the online validator   | http://examples.org |
        | sbol_compliant_uris          | Enables autoconstruction of SBOL-compliant URIs from displayIds          | True or False   |
        | sbol_typed_uris              | Include the SBOL type in SBOL-compliant URIs                             | True or False   |
        | output_format                | File format for serialization                                            | True or False   |
        | validate                     | Automatic validation                                                     | True or False   |
        | validate_online              | Use online (not local) validator for validation and conversion requests  | True or False, defaults to True   |
        | validator_url                | The http request endpoint for online validation and conversion           | A valid URL, set to<br>https://validator.sbolstandard.org/validate/ by default |
        | java_location                | Path to Java executable for offline validation and conversion            | A valid URL, set to<br>/usr/bin/java by default |
        | language                     | File format for conversion                                               | SBOL2, SBOL1, FASTA, GenBank |
        | test_equality                | Report differences between two files                                     | True or False |
        | check_uri_compliance         | If set to false, URIs in the file will not be checked for compliance<br>with the SBOL specification | True or False |
        | check_completeness           | If set to false, not all referenced objects must be described within<br>the given main_file | True or False |
        | check_best_practices         | If set to true, the file is checked for the best practice rules set<br>in the SBOL specification | True or False |
        | fail_on_first_error          | If set to true, the validator will fail at the first error               | True or False |
        | provide_detailed_stack_trace | If set to true (and failOnFirstError is true) the validator will<br>provide a stack trace for the first validation error | True or False |
        | uri_prefix                   | Required for conversion from FASTA and GenBank to SBOL1 or SBOL2,<br>used to generate URIs  | True or False |
        | version                      | Adds the version to all URIs and to the document                         | A valid Maven version string |
        | return_file                  | Whether or not to return the file contents as a string                   | True or False |
        :param option: The option key
        :param val: The option value (str or bool expected)
        :return: None
        """
        # Convert a config option to its string value
        if isinstance(option, ConfigOptions):
            option = option.value
        # ca-path is deprecated. It is no longer needed in native python
        if option == 'ca-path':
            warnings.warn('ca-path is no longer used', DeprecationWarning)
            return
        if option not in options:
            msg = '{!r} is not a valid configuration option'.format(option)
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)
        if option in valid_options:
            if val in valid_options[option]:
                options[option] = val
            else:
                msg = '{!r} is not a valid value for option {!r}.'.format(val, option)
                msg += ' Valid options are: {!r}.'.format(valid_options[option])
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)
        else:
            # Any argument is valid, eg. uriPrefix
            options[option] = val

    @staticmethod
    def getOption(option):
        """Get current option value for online validation and conversion

        :param option: The option key
        :return: The option value
        """
        # Convert a config option to its string value
        if isinstance(option, ConfigOptions):
            option = option.value
        # ca-path is deprecated. It is no longer needed in native python
        if option == 'ca-path':
            warnings.warn('ca-path is no longer used', DeprecationWarning)
            return ''
        if option in options:
            return options[option]
        else:
            msg = '{!r} is not a valid configuration option'.format(option)
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT, msg)


# Global methods
def setHomespace(ns):
    Config.setHomespace(ns)


def getHomespace():
    return Config.getHomespace()


def hasHomespace():
    return Config.hasHomespace()


def setFileFormat(file_format):
    Config.setFileFormat(file_format)


def getFileFormat():
    return Config.getFileFormat()


# constructCompliantURI is never invoked. If it ever gets resurrected,
# fix the use of os.sep.
#
# def constructCompliantURI(sbol_type, display_id, version):
#     if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
#         return getHomespace() + os.sep + parseClassName(sbol_type) + os.sep + \
#                display_id + os.sep + version
#     else:
#         return ''


# constructCompliantURI_parentChild is never invoked. If it ever gets
# resurrected, fix the use of os.sep.
#
# def constructCompliantURI_parentChild(parent_type, child_type,
#                                       display_id, version):
#     if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
#         return getHomespace() + os.sep + parseClassName(parent_type) + \
#                os.sep + parseClassName(child_type) + \
#                os.sep + display_id + os.sep + version
#     else:
#         return ''


# randomIdentifier is only invoked by autoconstructURI below, and
# autoconstructURI is never called. Delete this function when
# autoconstructURI is deleted.
#
# def randomIdentifier():
#     # TODO test
#     id = ''
#     for i in range(1, 11):
#         r = random.randint(0, 9)
#         id += str(r)
#         if r % 4 == 0 and r != 16:
#             id += '-'
#     return id


# autoconstructURI is never invoked. If it ever gets resurrected, fix
# the use of os.sep.
#
# def autoconstructURI():
#     if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS) is False \
#             and hasHomespace():
#         return getHomespace() + os.sep + randomIdentifier()
#     elif Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS) is False \
#             and not hasHomespace():
#         raise SBOLError('The autoconstructURI method requires '
#                         'a valid namespace authority. Use setHomespace().',
#                         SBOLErrorCode.SBOL_ERROR_COMPLIANCE)
#     else:
#         raise SBOLError('The autoconstructURI method only works '
#                         'when SBOLCompliance flag is false. '
#                         'Use setOption to disable SBOL-compliant URIs.',
#                         SBOLErrorCode.SBOL_ERROR_COMPLIANCE)


# getCompliantURI is never invoked. If it ever gets resurrected, fix
# the use of os.sep.
#
# def getCompliantURI(uri_prefix, sbol_class_name, display_id, version):
#     return uri_prefix + os.sep + sbol_class_name + \
#            os.sep + display_id + os.sep + version


def parseClassName(uri):
    if '#' in uri:
        return uri[uri.rindex('#')+1:]
    elif '/' in uri:
        return uri[uri.rindex('/')+1:]
    else:
        return ''


def parseNamespace(uri):
    if '#' in uri:
        return uri[:uri.rindex('#')]
    elif '/' in uri:
        return uri[:uri.rindex('/')]
    else:
        return ''


def parseURLDomain(url):
    protocol, path = url.split('://')
    path = path.split('/')[0]
    url = '://'.join([protocol, path])
    return url


def parsePropertyName(uri):
    return parseClassName(uri)


def string_equal(str1: Any, str2: Any) -> bool:
    """Converts the two arguments to str and compares them, returning
    the result. This helps when comparing a str with a rdflib.URIRef
    or a rdflib.Literal.
    """
    return str(str1) == str(str2)
