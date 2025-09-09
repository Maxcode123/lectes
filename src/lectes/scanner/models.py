from dataclasses import dataclass

from lectes.config.models import Rule


@dataclass
class Token:
    rule: Rule
    literal: str

    @property
    def name(self) -> str:
        return self.rule.name
