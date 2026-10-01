from typing import Callable, Generator, Any

from lectes.config.models import Configuration, Rule
from lectes.scanner.models import Token
from lectes.scanner.logger import Logger, LogLevel


class Scanner:
    """
    Scans a given text and returns tokens based on the provided configuration.

    At each position the scanner picks the rule with the longest match; if
    several rules match the same length, the one configured first wins. Within
    a single rule, matching follows Python's `re` semantics (leftmost-first),
    so a pattern like `a|ab` matches only `a`.

    ## Example

    ```python
    from lectes import Rule, Configuration, Regex, Scanner

    config = Configuration(
        [
            Rule(name="FOR", regex=Regex("for")),
            Rule(name="INT", regex=Regex("[1-9]+")),
            Rule(name="ID", regex=Regex("[a-zA-Z][a-zA-Z0-9]*")),
            Rule(name="WHITESPACE", regex=Regex("( )")),
        ]
    )

    scanner = Scanner(config)
    program = "somevar in othervar for 9 let"

    for token in scanner.scan(program):
        print(token)
    ```
    """

    def __init__(self, configuration: Configuration, debug: bool = False) -> None:
        self.configuration = configuration
        self._unmatched_handler = self._handle_unmatched
        self._matched_handlers = {
            rule: self._handle_matched for rule in configuration.rules
        }
        self._debug = debug
        self._logger = None

    def scan(self, text: str) -> Generator[Token]:
        """
        Scan the given text and yield tokens as they are recognized.

        Each contiguous run of text not matched by any rule is passed to the
        unmatched handler as a single string.
        """
        position = 0
        unmatched_start = None

        while position < len(text):
            rule, literal = self._longest_match(text, position)

            if rule is None:
                if unmatched_start is None:
                    unmatched_start = position

                position += 1
                continue

            if unmatched_start is not None:
                self._flush_unmatched(text[unmatched_start:position])
                unmatched_start = None

            self.logger().debug(f"rule {rule.name} matched: '{literal}'")
            result = self._matched_handlers[rule](literal, rule)

            if result is not None:
                yield result

            position += len(literal)

        if unmatched_start is not None:
            self._flush_unmatched(text[unmatched_start:])

    def set_unmatched_handler(self, handler: Callable[[str], None]) -> None:
        """
        Set the given function as the handler that executes when a string is not
        matched to a configured rule.

        The handler receives the string as argument and does returns None.
        """
        self._unmatched_handler = handler

    def set_handler(self, rule: Rule, handler: Callable[[str, Rule], Any]) -> None:
        """
        Set the given function as the handler that executes when a string is matched
        against rule.

        The handler should receive the matched string literal and the rule as arguments.
        """
        self._matched_handlers[rule] = handler

    def logger(self) -> Logger:
        """
        Return the scanner's logger instance.
        """
        if self._logger is None:
            self._logger = self._build_logger()

        return self._logger

    def _build_logger(self) -> Logger:
        logger = Logger()

        if self._debug:
            logger.set_level(LogLevel.DEBUG)

        return logger

    def _longest_match(self, text: str, position: int) -> tuple[Rule | None, str]:
        best_rule = None
        best_literal = ""

        for rule in self.configuration.rules:
            literal = rule.regex.match_prefix(text, position)

            # Empty matches never produce tokens; ties go to the earlier rule.
            if literal and len(literal) > len(best_literal):
                best_rule = rule
                best_literal = literal

        return best_rule, best_literal

    def _flush_unmatched(self, unmatched: str) -> None:
        self.logger().debug(f"unmatched: '{unmatched}'")
        self._unmatched_handler(unmatched)

    @staticmethod
    def _handle_unmatched(unmatched: str) -> None:
        print(f"unmatched: {unmatched}")

    @staticmethod
    def _handle_matched(matched: str, rule: Rule) -> Token:
        return Token(rule=rule, literal=matched)
