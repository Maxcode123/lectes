from dataclasses import dataclass

from lectes.engine.models import Regex


@dataclass
class Rule:
    name: str
    regex: Regex


@dataclass
class Configuration:
    rules: list[Rule]
