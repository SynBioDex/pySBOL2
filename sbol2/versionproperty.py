from .property import LiteralProperty
import packaging.version as pv
import rdflib


class VersionProperty(LiteralProperty):

    def convert_to_user(self, value):
        result = str(value)
        if result == '':
            # special case, empty strings are equivalent to None
            return None
        return result

    def convert_from_user(self, value):
        # Empty string is equivalent to None
        if value == '':
            value = None
        # None is ok iff upper bound is 1 and lower bound is 0.
        # If upper bound > 1, attribute is a list and None is not a valid list
        # If lower bound > 0, attribute must have a value, so None is unacceptable
        if value is None and self.upper_bound == 1 and self.lower_bound == 0:
            return None
        try:
            version = pv.Version(value)
        except pv.InvalidVersion as e:
            raise ValueError(e)
        except TypeError as e:
            raise ValueError(e)
        return rdflib.Literal(str(version))

    @staticmethod
    def _make_version(major: int, minor: int, micro: int) -> pv.Version:
        return pv.Version(f'{major}.{minor}.{micro}')

    @staticmethod
    def increment_major(version: str) -> str:
        old = pv.Version(version)
        new = VersionProperty._make_version(old.major + 1, old.minor, old.micro)
        return str(new)
