from unittest_extensions import args, TestCase

from lectes.engine.models import Regex
from lectes.engine.errors import RegexPatternError


class TestRegexMatchPrefix(TestCase):
    def subject(self, pattern, string="", pos=0):
        return Regex(pattern).match_prefix(string, pos)

    def assert_matched(self, literal):
        self.assertResult(literal)

    def assert_no_match(self):
        self.assertResultIs(None)

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
    def test_simple_char_at_start(self):
        self.assert_matched("a")

    @args(pattern="a", string="bcd")
    def test_simple_char_absence_in_string(self):
        self.assert_no_match()

    @args(pattern="for", string="for i in a:")
    def test_word_occurence(self):
        self.assert_matched("for")

    @args(pattern="for", string="a: int = 2")
    def test_word_absence(self):
        self.assert_no_match()

    @args(pattern="for", string="forum")
    def test_word_occurence_in_substring(self):
        self.assert_matched("for")

    @args(pattern="for", string="a for")
    def test_word_later_in_string_is_not_matched(self):
        self.assert_no_match()

    @args(pattern="for", string="a for", pos=2)
    def test_word_at_given_position(self):
        self.assert_matched("for")

    @args(pattern="for", string="a for", pos=1)
    def test_match_is_anchored_at_given_position(self):
        self.assert_no_match()

    @args(pattern="a", string="a", pos=1)
    def test_position_at_end_of_string(self):
        self.assert_no_match()

    @args(pattern="a*", string="b")
    def test_empty_match(self):
        self.assert_matched("")

    @args(pattern="ab|cd", string="abd")
    def test_character_alternation(self):
        self.assert_matched("ab")

    @args(pattern="ab|cd", string="aca")
    def test_alternation_does_not_match(self):
        self.assert_no_match()

    @args(pattern="ab|cd", string="cd")
    def test_character_alternation_presedence(self):
        self.assert_matched("cd")

    @args(pattern="ab|abc|abcd", string="abcde")
    def test_multiple_alternation_takes_first_alternative(self):
        self.assert_matched("ab")

    @args(pattern="this|that", string="this or that")
    def test_alternation_first_match(self):
        self.assert_matched("this")

    @args(pattern="a?b", string="bcd")
    def test_zero_or_one_zero(self):
        self.assert_matched("b")

    @args(pattern="a?b", string="abcd")
    def test_zero_or_one_one(self):
        self.assert_matched("ab")

    @args(pattern="a?b", string="cd")
    def test_zero_or_one_absence(self):
        self.assert_no_match()

    @args(pattern="a*b", string="bcd")
    def test_zero_or_more_zero(self):
        self.assert_matched("b")

    @args(pattern="a*b", string="abcd")
    def test_zero_or_more_one(self):
        self.assert_matched("ab")

    @args(pattern="a*b", string="aabcd")
    def test_zero_or_more_two(self):
        self.assert_matched("aab")

    @args(pattern="a*b", string="cd")
    def test_zero_or_more_absence(self):
        self.assert_no_match()

    @args(pattern="a+b", string="bcd")
    def test_one_or_more_zero(self):
        self.assert_no_match()

    @args(pattern="a+b", string="abcd")
    def test_one_or_more_one(self):
        self.assert_matched("ab")

    @args(pattern="a+b", string="aabcd")
    def test_one_or_more_two(self):
        self.assert_matched("aab")

    @args(pattern="[a-z]", string="k")
    def test_small_letter_class(self):
        self.assert_matched("k")

    @args(pattern="[a-z]", string="K")
    def test_small_letter_class_with_capital(self):
        self.assert_no_match()

    @args(pattern="[A-Z]", string="U")
    def test_capital_letter_class(self):
        self.assert_matched("U")

    @args(pattern="[a-d]", string="e")
    def test_letter_class_out_of_range(self):
        self.assert_no_match()

    @args(pattern="[a-z]", string=" ")
    def test_letter_class_with_whitespace(self):
        self.assert_no_match()

    @args(pattern="[A-Z]", string="y")
    def test_capital_letter_class_with_downcase(self):
        self.assert_no_match()

    @args(pattern="[0-4]", string="3")
    def test_numeric_class_in_range(self):
        self.assert_matched("3")

    @args(pattern="[2-7]", string="1")
    def test_numeric_class_out_of_range(self):
        self.assert_no_match()

    @args(pattern="[a-zA-Z]", string="b")
    def test_all_letters_compound_class(self):
        self.assert_matched("b")

    @args(pattern="[a-zA-Z]", string="G")
    def test_all_letters_compound_class_capital(self):
        self.assert_matched("G")

    @args(pattern="[a-zA-Z2-6]", string="5")
    def test_letter_and_numeric_class(self):
        self.assert_matched("5")


class TestRegexEquality(TestCase):
    def test_same_pattern_equal(self):
        self.assertEqual(Regex("a+"), Regex("a+"))

    def test_different_pattern_not_equal(self):
        self.assertNotEqual(Regex("a"), Regex("b"))

    def test_equal_regexes_have_equal_hashes(self):
        self.assertEqual(hash(Regex("a+")), hash(Regex("a+")))


class TestInvalidRegex(TestCase):
    def test_repr_of_invalid_pattern_does_not_raise(self):
        repr(Regex("("))
