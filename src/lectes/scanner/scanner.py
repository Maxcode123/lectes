from typing import Callable, Generator, Any, NoReturn

from lectes.config.models import Configuration, Rule
from lectes.scanner.errors import ScannerConfigurationError, UnmatchedTextError
from lectes.scanner.models import Location, Token, UnmatchedText
from lectes.scanner.logger import Logger, LogLevel


class Scanner:
    """
    Scans a given text and returns tokens based on the provided configuration.

    At each position the scanner picks the rule with the longest match; if
    several rules match the same length, the one configured first wins. Within
    a single rule, matching follows Python's `re` semantics (leftmost-first),
    so a pattern like `a|ab` matches only `a`.

    Text that no rule matches raises `UnmatchedTextError` by default. Pass
    `ignore_unmatched=True` to skip it instead, or set a custom handler with
    `set_unmatched_handler`.

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

    def __init__(
        self,
        configuration: Configuration,
        debug: bool = False,
        ignore_unmatched: bool = False,
    ) -> None:
        self.configuration = configuration
        self._ignore_unmatched = ignore_unmatched
        self._unmatched_handler: Callable[[UnmatchedText], None] = (
            self._handle_unmatched
        )
        self._matched_handlers = {
            rule: self._handle_matched for rule in configuration.rules
        }
        self._debug = debug
        self._logger = None

    def scan(self, text: str) -> Generator[Token]:
        """
        Scan the given text and yield tokens as they are recognized.

        Each contiguous run of text not matched by any rule is passed to the
        unmatched handler as a single `UnmatchedText`, once the run ends.

        Raises:
            UnmatchedTextError: if part of the text matches no rule, unless
                `ignore_unmatched` is set or a custom unmatched handler is used.
                Tokens before the unmatched text have already been yielded.
        """
        cursor = _Cursor()
        unmatched_location = None
        logger = self.logger()
        debug = logger.enabled()

        while cursor.offset < len(text):
            rule, literal = self._longest_match(text, cursor.offset)

            if rule is None:
                if unmatched_location is None:
                    unmatched_location = cursor.location()

                cursor.advance(text[cursor.offset])
                continue

            if unmatched_location is not None:
                self._flush_unmatched(
                    UnmatchedText(
                        text=text[unmatched_location.offset : cursor.offset],
                        location=unmatched_location,
                    )
                )
                unmatched_location = None

            if debug:
                logger.debug("rule %s matched: %r", rule.name, literal)

            token = Token(rule=rule, literal=literal, location=cursor.location())
            result = self._matched_handlers[rule](token)

            if result is not None:
                yield result

            cursor.advance(literal)

        if unmatched_location is not None:
            self._flush_unmatched(
                UnmatchedText(
                    text=text[unmatched_location.offset :],
                    location=unmatched_location,
                )
            )

    def set_unmatched_handler(self, handler: Callable[[UnmatchedText], None]) -> None:
        """
        Set the given function as the handler that executes when a string is not
        matched to a configured rule.

        The handler receives the `UnmatchedText` and returns None. It replaces the
        default behaviour of raising `UnmatchedTextError`.

        Raises:
            ScannerConfigurationError: if the scanner was created with
                `ignore_unmatched=True`, since the handler would never run.
        """
        if self._ignore_unmatched:
            raise ScannerConfigurationError(
                "cannot set an unmatched handler on a scanner that ignores "
                "unmatched text"
            )

        self._unmatched_handler = handler

    def set_handler(self, rule: Rule, handler: Callable[[Token], Any]) -> None:
        """
        Set the given function as the handler that executes when a string is matched
        against rule.

        The handler receives the matched Token. Whatever it returns, except None,
        is yielded by `scan`; returning None skips the token.
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

    def _flush_unmatched(self, unmatched: UnmatchedText) -> None:
        self.logger().debug("unmatched: %r", unmatched.text)

        if self._ignore_unmatched:
            return

        self._unmatched_handler(unmatched)

    @staticmethod
    def _handle_unmatched(unmatched: UnmatchedText) -> NoReturn:
        raise UnmatchedTextError(unmatched)

    @staticmethod
    def _handle_matched(token: Token) -> Token:
        return token


class _Cursor:
    """
    Tracks the offset, line and column of the scanner while it reads a text.
    """

    def __init__(self) -> None:
        self.offset = 0
        self._line = 1
        self._line_start = 0

    def location(self) -> Location:
        return Location(
            offset=self.offset,
            line=self._line,
            column=self.offset - self._line_start + 1,
        )

    def advance(self, consumed: str) -> None:
        newlines = consumed.count("\n")

        if newlines:
            self._line += newlines
            self._line_start = self.offset + consumed.rfind("\n") + 1

        self.offset += len(consumed)
