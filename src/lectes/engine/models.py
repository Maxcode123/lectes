from __future__ import annotations
from dataclasses import dataclass
import re

from lectes.engine.errors import RegexPatternError


@dataclass
class Match:
    unmatched: str | None
    string: str
    re: "Regex"

    @classmethod
    def from_re(cls, match: re.Match) -> "Match":
        index = match.span()
        matched = match.string[index[0] : index[1]]
        unmatched = match.string.replace(matched, "")
        unmatched = unmatched if len(unmatched) >= 1 else None
        return Match(unmatched=unmatched, string=matched, re=Regex.from_re(match.re))

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.string)


class Regex:
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._re_pattern = None

    @classmethod
    def from_re(cls, pattern: re.Pattern) -> "Regex":
        return Regex(pattern.pattern)

    def fullmatch(self, string: str) -> Match | None:
        match = self._compiled_pattern().fullmatch(string)

        if match is None:
            return None

        return Match.from_re(match)

    def search(self, string: str) -> Match | None:
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
