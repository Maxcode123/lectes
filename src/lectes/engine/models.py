from __future__ import annotations
from dataclasses import dataclass
import re

from lectes.engine.errors import RegexPatternError


@dataclass
class Match:
    """
    Represents a regular expression match.

    Objects hold the matched string, the unmatched part of the string they were
    checked against and the actual Regex object.
    """

    unmatched: str | None
    string: str
    re: "Regex"

    @classmethod
    def from_re(cls, match: re.Match) -> "Match":
        """
        Create an object from Python's standard library re.Match object.
        """

        index = match.span()
        matched = match.string[index[0] : index[1]]
        unmatched = match.string.replace(matched, "")
        unmatched = unmatched if len(unmatched) >= 1 else None
        return Match(unmatched=unmatched, string=matched, re=Regex.from_re(match.re))

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.string)


@dataclass(init=False)
class Regex:
    """
    Represents a regular expression.

    Can be initialized with any string, but upon invoking a method, the validity
    of the string will be checked and may raise an error.
    """

    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._re_pattern = None

    @classmethod
    def from_re(cls, pattern: re.Pattern) -> "Regex":
        """
        Create an object from Python's standard library re.Pattern object.
        """
        return Regex(pattern.pattern)

    def fullmatch(self, string: str) -> Match | None:
        """
        If the whole string matches the regular expression, return a Match.
        Return None if the string does not match the regular expression.
        """
        match = self._compiled_pattern().fullmatch(string)

        if match is None:
            return None

        return Match.from_re(match)

    def search(self, string: str) -> Match | None:
        """
        Scan through string looking for the first location where the regular
        expression pattern produces a match, and return a Match. Return None if
        no position in the string matches the regular expression.
        """
        match = self._compiled_pattern().search(string)

        if match is None:
            return None

        return Match.from_re(match)

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
        return f"<Regex: {self._compiled_pattern().pattern}>"

    def __hash__(self) -> int:
        return hash(self._pattern)
