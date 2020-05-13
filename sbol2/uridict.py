import collections
from typing import Any


class URIDict(collections.UserDict):

    def __init__(self):
        super().__init__()

    def __getitem__(self, key: str) -> Any:
        return super().__getitem__(str(key))

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(str(key), value)

    def __delitem__(self, key: str) -> None:
        super().__delitem__(str(key))

    def __contains__(self, key: str) -> bool:
        return super().__contains__(str(key))
