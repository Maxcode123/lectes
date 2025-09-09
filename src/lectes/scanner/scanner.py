from typing import Callable, Generator

from lectes.config.models import Configuration
from lectes.scanner.models import Token


class Scanner:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.set_program("")
        self._unmatched_handler = self._handle_unmatched

    def scan(self, program: str) -> Generator[Token]:
        if len(program) == 0:
            return

        self.set_program(program)

        self.current_position = 1
        for _ in program:
            for rule in self.configuration.rules:
                current_string = self.current_string()

                if match := rule.regex.search(current_string):
                    if match.unmatched is not None:
                        self._unmatched_handler(match.unmatched)
                    yield Token(rule=rule, literal=match.string)
                    self.last_position = self.current_position

            self.current_position += 1

    def set_unmatched_handler(self, handler: Callable[[str], None]) -> None:
        self._unmatched_handler = handler

    def set_program(self, program: str) -> None:
        self.program = program
        self.current_position = 0
        self.last_position = 0

    def current_string(self) -> str:
        return self.program[self.last_position : self.current_position]

    @staticmethod
    def _handle_unmatched(unmatched: str) -> None:
        print(f"unmatched: {unmatched}")
