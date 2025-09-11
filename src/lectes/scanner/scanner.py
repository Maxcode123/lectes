from typing import Callable, Generator

from lectes.config.models import Configuration
from lectes.scanner.models import Token
from lectes.scanner.logger import Logger, LogLevel


class Scanner:
    def __init__(self, configuration: Configuration, debug: bool = False) -> None:
        self.configuration = configuration
        self.set_text("")
        self._unmatched_handler = self._handle_unmatched
        self._debug = debug
        self._logger = None

    def scan(self, text: str) -> Generator[Token]:
        if len(text) == 0:
            return

        self.set_text(text)

        for character in text:
            self.logger().debug(f"character: '{character}'")

            current_string = self.current_string()
            self.logger().debug(f"current_string: '{current_string}'")

            lookahead_string = self.lookahead_string()
            self.logger().debug(f"lookahead_string: '{lookahead_string}'")

            for rule in self.configuration.rules:
                if not self._is_last_char() and rule.regex.fullmatch(lookahead_string):
                    self.logger().debug(
                        f"rule {rule.name} fullmatched lookahead_string: '{lookahead_string}'"
                    )
                    break

                if match := rule.regex.search(current_string):
                    self.logger().debug(
                        f"rule {rule.name} matched current_string: '{current_string}'"
                    )

                    if match.unmatched is not None:
                        self._unmatched_handler(match.unmatched)

                    yield Token(rule=rule, literal=match.string)

                    self.last_position = self.current_position
                    break

            self.current_position += 1

    def set_unmatched_handler(self, handler: Callable[[str], None]) -> None:
        self._unmatched_handler = handler

    def set_text(self, text: str) -> None:
        self.text = text
        self.current_position = 1
        self.last_position = 0

    def current_string(self) -> str:
        return self.text[self.last_position : self.current_position]

    def lookahead_string(self) -> str:
        return self.text[self.last_position : self.current_position + 1]

    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = self._build_logger()

        return self._logger

    def _build_logger(self) -> Logger:
        logger = Logger()

        if self._debug:
            logger.set_level(LogLevel.DEBUG)

        return logger

    def _is_last_char(self) -> bool:
        return self.current_position == len(self.text)

    @staticmethod
    def _handle_unmatched(unmatched: str) -> None:
        print(f"unmatched: {unmatched}")
