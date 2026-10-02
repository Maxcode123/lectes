from lectes.errors import LectesError


class GrammarError(LectesError):
    """
    The grammar text passed to `Configuration.from_text` is invalid.

    Every error found is available as `problems`, a list of `(line, message)`
    pairs. `line` is 1-based, or None when the problem isn't tied to a line.
    """

    def __init__(self, problems: list[tuple[int | None, str]]) -> None:
        super().__init__(
            "\n".join(
                message if line is None else f"line {line}: {message}"
                for line, message in problems
            )
        )
        self.problems = problems


class GrammarWarning(UserWarning):
    """
    The grammar text passed to `Configuration.from_text` is valid but probably
    not what was intended.

    The 1-based grammar line is available as `line` and the text as `message`.
    """

    def __init__(self, line: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.message = message
