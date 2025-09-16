from dataclasses import dataclass

from lectes.config.models import Rule


@dataclass
class Token:
    """
    Represents a token returned by the scanner.

    The scanned token is related to a configuration rule and a string literal.
    """

    rule: Rule
    literal: str

    @property
    def name(self) -> str:
        return self.rule.name
