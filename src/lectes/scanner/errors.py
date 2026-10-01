from lectes.errors import LectesError
from lectes.scanner.models import UnmatchedText


class ScannerError(LectesError):
    """
    Base class for all errors occuring in the scanner.
    """


class ScannerConfigurationError(ScannerError):
    """
    The scanner has been configured in a conflicting way.
    """


class UnmatchedTextError(ScannerError):
    """
    Part of the scanned text does not match any configured rule.

    The unmatched text and its location are available as `unmatched`.
    """

    def __init__(self, unmatched: UnmatchedText) -> None:
        location = unmatched.location
        super().__init__(
            f"unmatched text {unmatched.text!r} "
            f"at line {location.line}, column {location.column}"
        )
        self.unmatched = unmatched
