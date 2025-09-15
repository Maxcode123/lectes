from re import Pattern
from unittest_extensions import args, TestCase

from lectes.engine.models import Regex
from lectes.engine.errors import RegexPatternError


class TestRegexSearch(TestCase):
    def subject(self, pattern, string=""):
        return Regex(pattern).search(string)

    def assert_unmatched(self, unmatched):
        self.assertResultTrue()
        self.assertSequenceEqual(self.cachedResult().unmatched, unmatched)

    def assert_pattern_error(self):
        with self.assertRaises(RegexPatternError):
            self.result()

    @args(pattern="(")
    def test_unclosed_parentheses(self):
        self.assert_pattern_error()

    @args(pattern="[a-Z]")
    def test_all_letters_class(self):
        self.assert_pattern_error()

    @args(pattern="a", string="a b a")
    def test_simple_char_two_occurences_in_string(self):
        self.assert_unmatched(" b ")

    @args(pattern="a", string="bcd")
    def test_simple_char_absence_in_string(self):
        self.assertResultFalse()

    @args(pattern="for", string="for i in a:")
    def test_word_occurence(self):
        self.assertResultTrue()

    @args(pattern="for", string="a: int = 2")
    def test_word_absence(self):
        self.assertResultFalse()

    @args(pattern="for", string="forum")
    def test_word_occurence_in_substring(self):
        self.assertResultTrue()

    @args(pattern="ab|cd", string="abd")
    def test_character_alternation(self):
        self.assert_unmatched("d")

    @args(pattern="ab|cd", string="aca")
    def test_alternation_does_not_match(self):
        self.assertResultFalse()

    @args(pattern="ab|cd", string="cd")
    def test_character_alternation_presedence(self):
        self.assertResultTrue()

    @args(pattern="ab|abc|abcd", string="abcde")
    def test_multiple_alternation(self):
        self.assert_unmatched("cde")

    @args(pattern="this|that", string="this or that")
    def test_alternation_first_match(self):
        self.assert_unmatched(" or that")

    @args(pattern="a?b", string="bcd")
    def test_zero_or_one_zero(self):
        self.assert_unmatched("cd")

    @args(pattern="a?b", string="abcd")
    def test_zero_or_one_one(self):
        self.assert_unmatched("cd")

    @args(pattern="a?b", string="cd")
    def test_zero_or_one_absence(self):
        self.assertResultFalse()

    @args(pattern="a*b", string="bcd")
    def test_zero_or_more_zero(self):
        self.assert_unmatched("cd")

    @args(pattern="a*b", string="abcd")
    def test_zero_or_more_one(self):
        self.assert_unmatched("cd")

    @args(pattern="a*b", string="aabcd")
    def test_zero_or_more_two(self):
        self.assert_unmatched("cd")

    @args(pattern="a*b", string="cd")
    def test_zero_or_more_absence(self):
        self.assertResultFalse()

    @args(pattern="a+b", string="bcd")
    def test_one_or_more_zero(self):
        self.assertResultFalse()

    @args(pattern="a+b", string="abcd")
    def test_one_or_more_one(self):
        self.assert_unmatched("cd")

    @args(pattern="a+b", string="aabcd")
    def test_one_or_more_two(self):
        self.assert_unmatched("cd")

    @args(pattern="[a-z]", string="k")
    def test_small_letter_class(self):
        self.assertResultTrue()

    @args(pattern="[a-z]", string="K")
    def test_small_letter_class_with_capital(self):
        self.assertResultFalse()

    @args(pattern="[A-Z]", string="U")
    def test_capital_letter_class(self):
        self.assertResultTrue()

    @args(pattern="[a-d]", string="e")
    def test_letter_class_out_of_range(self):
        self.assertResultFalse()

    @args(pattern="[a-z]", string=" ")
    def test_letter_class_with_whitespace(self):
        self.assertResultFalse()

    @args(pattern="[A-Z]", string="y")
    def test_capital_letter_class_with_downcase(self):
        self.assertResultFalse()

    @args(pattern="[0-4]", string="3")
    def test_numeric_class_in_range(self):
        self.assertResultTrue()

    @args(pattern="[2-7]", string="1")
    def test_numeric_class_out_of_range(self):
        self.assertResultFalse()

    @args(pattern="[a-zA-Z]", string="b")
    def test_all_letters_compound_class(self):
        self.assertResultTrue()

    @args(pattern="[a-zA-Z]", string="G")
    def test_all_letters_compound_class_capital(self):
        self.assertResultTrue()

    @args(pattern="[a-zA-Z2-6]", string="5")
    def test_letter_and_numeric_class(self):
        self.assertResultTrue()
