from dataclasses import dataclass

from lectes.config.models import Rule


@dataclass(frozen=True)
class Location:
    """
    Represents where a piece of the scanned text starts.

    The offset is 0-based; line and column are 1-based. Columns count
    characters, so a tab counts as one column, and only `\\n` starts a new line.
    """

    offset: int
    line: int
    column: int


@dataclass(frozen=True)
class Token:
    """
    Represents a token returned by the scanner.

    The scanned token is related to a configuration rule, a string literal and
    the location in the text where the literal starts.
    """

    rule: Rule
    literal: str
    location: Location

    @property
    def name(self) -> str:
        return self.rule.name
