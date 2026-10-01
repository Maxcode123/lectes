from unittest import TestCase

import lectes
from lectes.engine.errors import RegexPatternError
from lectes.errors import LectesError
from lectes.scanner.errors import (
    ScannerConfigurationError,
    ScannerError,
    UnmatchedTextError,
)
from lectes.scanner.models import Location, Token, UnmatchedText


class TestPackageExports(TestCase):
    def test_models_are_exported(self):
        self.assertIs(lectes.Token, Token)
        self.assertIs(lectes.Location, Location)
        self.assertIs(lectes.UnmatchedText, UnmatchedText)

    def test_errors_are_exported(self):
        self.assertIs(lectes.LectesError, LectesError)
        self.assertIs(lectes.RegexPatternError, RegexPatternError)
        self.assertIs(lectes.ScannerError, ScannerError)
        self.assertIs(lectes.ScannerConfigurationError, ScannerConfigurationError)
        self.assertIs(lectes.UnmatchedTextError, UnmatchedTextError)
