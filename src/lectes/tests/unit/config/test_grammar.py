import warnings
from unittest_extensions import args, TestCase

import lectes
from lectes.config.errors import GrammarError, GrammarWarning
from lectes.config.models import Configuration, Rule
from lectes.engine.models import Regex
from lectes.errors import LectesError


class TestFromText(TestCase):
    def subject(self, text):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.warnings = caught
            return Configuration.from_text(text)

    def assert_rules(self, *rules):
        self.assertSequenceEqual(
            self.result().rules,
            [Rule(name=name, regex=Regex(pattern)) for name, pattern in rules],
        )

    def assert_problems(self, *problems):
        with self.assertRaises(GrammarError) as context:
            self.result()

        self.assertSequenceEqual(context.exception.problems, problems)

    def assert_warnings(self, *problems):
        self.result()
        self.assertTrue(all(w.category is GrammarWarning for w in self.warnings))
        self.assertSequenceEqual(
            [(w.message.line, w.message.message) for w in self.warnings], problems
        )


class TestFromTextRules(TestFromText):
    @args("FOR for\nID [a-z]+\n")
    def test_one_rule_per_line(self):
        self.assert_rules(("FOR", "for"), ("ID", "[a-z]+"))

    @args("# header\n\n   # indented\nID [a-z]+\n\n")
    def test_skips_blank_lines_and_comments(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("ID [a-z]+")
    def test_space_separates_name_and_pattern(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("ID\t[a-z]+")
    def test_tab_separates_name_and_pattern(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("ID  \t  [a-z]+")
    def test_mixed_whitespace_separates_name_and_pattern(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("HASH  #[a-z]+ x\nSP  a b")
    def test_pattern_is_the_rest_of_the_line(self):
        self.assert_rules(("HASH", "#[a-z]+ x"), ("SP", "a b"))

    @args("ID [a-z]+   \t")
    def test_trailing_whitespace_is_stripped(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("   ID [a-z]+")
    def test_leading_whitespace_before_name_is_allowed(self):
        self.assert_rules(("ID", "[a-z]+"))

    @args("NUM [0-9]+\nNUM 0x[0-9a-f]+")
    def test_duplicate_names_are_allowed(self):
        self.assert_rules(("NUM", "[0-9]+"), ("NUM", "0x[0-9a-f]+"))

    @args("A a\r\nB b\r\n")
    def test_crlf_line_endings(self):
        self.assert_rules(("A", "a"), ("B", "b"))

    @args("A a\rB b\r")
    def test_cr_line_endings(self):
        self.assert_rules(("A", "a"), ("B", "b"))

    @args("GREEK [α-ω]+")
    def test_non_ascii_pattern(self):
        self.assert_rules(("GREEK", "[α-ω]+"))

    @args("KW (?i)select")
    def test_inline_flags(self):
        self.assert_rules(("KW", "(?i)select"))

    @args("FOR for\nID [a-z]+\n")
    def test_valid_grammar_has_no_warnings(self):
        self.assert_warnings()

    @args("\n".join(f"R{i} r{i}" for i in range(500)))
    def test_has_no_rule_limit(self):
        self.assertEqual(len(self.result().rules), 500)


class TestFromTextErrors(TestFromText):
    @args("9X a")
    def test_invalid_name(self):
        self.assert_problems((1, "invalid rule name '9X'"))

    @args("ID\nOK a")
    def test_name_without_pattern(self):
        self.assert_problems((1, "rule 'ID' has no pattern"))

    @args("ID   \nOK a")
    def test_name_with_only_whitespace_after_it(self):
        self.assert_problems((1, "rule 'ID' has no pattern"))

    @args("OK a\nID [a-")
    def test_regex_that_fails_to_compile(self):
        self.assert_problems((2, "rule 'ID': unterminated character set at position 0"))

    @args("")
    def test_empty_text(self):
        self.assert_problems((None, "grammar has no rules"))

    @args("\n\n")
    def test_only_blank_lines(self):
        self.assert_problems((None, "grammar has no rules"))

    @args("# only a comment\n")
    def test_only_comments(self):
        self.assert_problems((None, "grammar has no rules"))

    @args("9X a\nID\nOK a\nBAD (\nE x?")
    def test_reports_every_error(self):
        self.assert_problems(
            (1, "invalid rule name '9X'"),
            (2, "rule 'ID' has no pattern"),
            (4, "rule 'BAD': missing ), unterminated subpattern at position 0"),
        )

    @args("9X a")
    def test_errors_without_valid_rules_dont_add_no_rules_error(self):
        self.assert_problems((1, "invalid rule name '9X'"))

    @args("DEEP " + "(" * 2000 + "a" + ")" * 2000)
    def test_deeply_nested_pattern_does_not_crash_the_parser(self):
        try:
            self.result()
        except GrammarError:
            pass

    @args("9X a\nID")
    def test_error_message_lists_every_problem(self):
        with self.assertRaises(GrammarError) as context:
            self.result()

        self.assertEqual(
            str(context.exception),
            "line 1: invalid rule name '9X'\nline 2: rule 'ID' has no pattern",
        )

    @args("")
    def test_error_message_without_line(self):
        with self.assertRaises(GrammarError) as context:
            self.result()

        self.assertEqual(str(context.exception), "grammar has no rules")

    @args("")
    def test_error_is_a_lectes_error(self):
        self.assertResultRaises(LectesError)


class TestFromTextWarnings(TestFromText):
    @args("STAR a*")
    def test_empty_match_is_a_warning(self):
        self.assert_warnings(
            (1, "rule 'STAR' can match the empty string; empty matches are ignored")
        )

    @args("STAR a*")
    def test_rule_that_matches_empty_is_kept(self):
        self.assert_rules(("STAR", "a*"))

    @args("A a\nE x?\nF y*")
    def test_one_warning_per_problem(self):
        self.assert_warnings(
            (2, "rule 'E' can match the empty string; empty matches are ignored"),
            (3, "rule 'F' can match the empty string; empty matches are ignored"),
        )

    @args("STAR a*")
    def test_warning_str_is_the_message(self):
        self.result()
        self.assertEqual(
            str(self.warnings[0].message),
            "rule 'STAR' can match the empty string; empty matches are ignored",
        )

    @args("E x?\n9X a")
    def test_no_warnings_when_there_are_errors(self):
        self.assert_problems((2, "invalid rule name '9X'"))
        self.assertSequenceEqual(self.warnings, [])


class TestGrammarExports(TestCase):
    def test_errors_are_exported(self):
        self.assertIs(lectes.GrammarError, GrammarError)
        self.assertIs(lectes.GrammarWarning, GrammarWarning)
