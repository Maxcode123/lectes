import re

from lectes.engine.errors import RegexPatternError


class Regex:
    """
    Represents a regular expression.

    Can be initialized with any string, but upon invoking a method, the validity
    of the string will be checked and may raise an error.
    """

    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._re_pattern = None

    def match_prefix(self, string: str, pos: int = 0) -> str | None:
        """
        If the regular expression matches the string starting exactly at pos,
        return the matched text. Return None if there is no match at pos.
        """
        match = self._compiled_pattern().match(string, pos)

        if match is None:
            return None

        return match.group()

    def _compiled_pattern(self) -> re.Pattern:
        if self._re_pattern is None:
            self._re_pattern = self._compile_pattern()

        return self._re_pattern

    def _compile_pattern(self) -> re.Pattern:
        try:
            return re.compile(self._pattern)
        except re.PatternError as e:
            raise RegexPatternError(str(e)) from None

    def __repr__(self) -> str:
        return f"<Regex: {self._pattern}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Regex):
            return NotImplemented

        return self._pattern == other._pattern

    def __hash__(self) -> int:
        return hash(self._pattern)
