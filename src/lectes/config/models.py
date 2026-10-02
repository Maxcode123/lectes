import warnings
from dataclasses import dataclass
from typing import Self

from lectes.config.errors import GrammarError, GrammarWarning
from lectes.config.grammar import parse
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

    @classmethod
    def from_text(cls, text: str) -> Self:
        """
        Build a configuration from grammar text.

        The text has one rule per line: a name, whitespace, then the regex,
        which is the rest of the line. Blank lines and lines starting with `#`
        are ignored.

        ## Example

        ```python
        from lectes import Configuration

        config = Configuration.from_text(
            '''
            # arithmetic
            INT     [0-9]+
            PLUS    \\+
            WS      \\s+
            '''
        )
        ```

        Raises:
            GrammarError: if the text has any errors; every error found is
                listed in its `problems`.

        Warns:
            GrammarWarning: once per rule that is valid but probably not what
                was intended, such as one that can match the empty string.
        """
        grammar = parse(text)

        if grammar.errors:
            raise GrammarError(grammar.errors)

        for line, message in grammar.warnings:
            warnings.warn(GrammarWarning(line, message), stacklevel=2)

        return cls(
            [Rule(name=name, regex=Regex(pattern)) for name, pattern in grammar.rules]
        )
