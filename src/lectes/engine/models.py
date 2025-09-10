from __future__ import annotations
from dataclasses import dataclass
import re


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


class Regex:
    def __init__(self, pattern: str) -> None:
        self._pattern = re.compile(pattern)

    @classmethod
    def from_re(cls, pattern: re.Pattern) -> "Regex":
        return Regex(pattern.pattern)

    def search(self, string: str) -> Match | None:
        match = self._pattern.search(string)

        if match is None:
            return None

        return Match.from_re(match)

    def __repr__(self) -> str:
        return f"<Regex: {self._pattern.pattern}>"
