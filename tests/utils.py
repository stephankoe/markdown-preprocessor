from typing import Iterable, TypeVar

import regex as re

_T = TypeVar("_T")


def first(it: Iterable[_T], throw: bool = True, default: _T | None = None) -> _T:
    for elem in it:
        return elem

    if throw:
        raise ValueError("Iterator is empty.")
    return default


class MapReplacer:
    """A simple map-based replacer"""

    _GROUP_PREFIX = "group"

    def __init__(self, replacements: dict[str, str]):
        patterns = []
        self._replacements = {}
        for i, (pattern, replacement) in enumerate(replacements.items()):
            group_name = f"{self._GROUP_PREFIX}{i}"
            patterns.append(f"(?P<{group_name}>{pattern})")
            self._replacements[group_name] = replacement
        self._pattern = re.compile('|'.join(patterns))

    def find(self, text: str) -> Iterable[tuple[re.Match, int, int]]:
        for match in self._pattern.finditer(text):
            yield match, match.start(), match.end()

    def replace(self, match: re.Match) -> str:
        group_name = first(group_name
                           for group_name, value in match.groupdict().items()
                           if group_name in self._replacements
                           and value is not None)
        return self._replacements[group_name]
