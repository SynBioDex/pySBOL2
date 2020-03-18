from enum import Enum
import warnings


class SBOLErrorCode(Enum):
    DUPLICATE_URI_ERROR = 1
    NOT_FOUND_ERROR = 2
    SBOL_ERROR_NOT_FOUND = 3
    END_OF_LIST = 4
    SBOL_ERROR_END_OF_LIST = 5
    SBOL_ERROR_SERIALIZATION = 6
    SBOL_ERROR_PARSE = 7
    SBOL_ERROR_MISSING_NAMESPACE = 8
    SBOL_ERROR_NONCOMPLIANT_VERSION = 9
    SBOL_ERROR_COMPLIANCE = 10
    SBOL_ERROR_MISSING_DOCUMENT = 11
    SBOL_ERROR_INVALID_ARGUMENT = 12
    SBOL_ERROR_FILE_NOT_FOUND = 13
    SBOL_ERROR_ORPHAN_OBJECT = 14
    SBOL_ERROR_TYPE_MISMATCH = 15
    SBOL_ERROR_BAD_HTTP_REQUEST = 16
    SBOL_ERROR_URI_NOT_UNIQUE = 17
    SBOL_ERROR_HTTP_UNAUTHORIZED = 18


class SBOLError(Exception):

    def __init__(self, message, err):
        if isinstance(message, SBOLErrorCode):
            warnings.warn("SBOLError arguments out of order",
                          RuntimeWarning)
        self._message = message
        self._err = err

    def what(self):
        return self._message

    def error_code(self):
        return self._err
