from dataclasses import dataclass

from lectes.engine.models import Regex


@dataclass(frozen=True)
class Rule:
    """
    Represents a scanner configuration rule.

    Is actually a proxy for a regular expression.

    ## Example

    ```python
    from lectes import Regex

    Rule(name="INT_LITERAL", regex=Regex("0|([-]?[1-9]+[0-9]*))
    ```
    """

    name: str
    regex: Regex


@dataclass
class Configuration:
    """
    Represents the configured rules of the scanner.
    """

    rules: list[Rule]
