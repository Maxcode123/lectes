from typing import Literal
from unittest_extensions import args, TestCase

from lectes.config.models import Rule, Configuration
from lectes.engine.models import Regex
from lectes.engine.errors import RegexPatternError
from lectes.scanner.scanner import Scanner


def rule(name, regex):
    return Rule(name=name, regex=Regex(regex))


class TestScanner(TestCase):
    def subject(self, text):
        self.unmatched = []
        scanner = self.scanner()
        scanner.set_unmatched_handler(self.unmatched.append)
        return list(scanner.scan(text))

    def scanner(self):
        return Scanner(self.configuration())

    def configuration(self):
        return Configuration(self.rules())

    def assert_tokens(self, *tokens):
        self.assertSequenceEqual(list(map(lambda t: t.name, self.result())), tokens)

    def assert_literals(self, *literals):
        self.assertSequenceEqual([t.literal for t in self.result()], literals)

    def assert_unmatched(self, *unmatched):
        self.result()
        self.assertSequenceEqual(self.unmatched, unmatched)


class TestScannerSimpleGrammar(TestScanner):
    def rules(self):
        return [
            rule("FOR", "for"),
            rule("INT_LITERAL", "[0-9]+"),
            rule("INT", "int"),
            rule("ID", "[a-zA-Z][a-zA-Z0-9]*"),
            rule("WHITESPACE", "( )"),
        ]

    @args("somevar in othervar for 9 let")
    def test_scan(self):
        self.assert_tokens(
            "ID",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "FOR",
            "WHITESPACE",
            "INT_LITERAL",
            "WHITESPACE",
            "ID",
        )

    @args("int myint ")
    def test_longer_match(self):
        self.assert_tokens("INT", "WHITESPACE", "ID", "WHITESPACE")


class TestScannerClassicGrammar(TestScanner):
    def rules(self):
        return [
            rule("OPER", "oper"),
            rule("EXEMP", "exemp"),
            rule("INT", "int"),
            rule("DUPL", "dupl"),
            rule("STR", "str"),
            rule("ANEF", "anef"),
            rule("EGO", "ego"),
            rule("INITUS", "initus"),
            rule("EXODUS", "exodus"),
            rule("ID", "(_|[a-zA-Z])(_|[a-zA-Z0-9])*"),
            rule("INT_LITERAL", "[-]?[0-9]+"),
            rule("DOUBLE_LITERAL", "[-+]?[0-9]+\.?[0-9]*"),
            rule("PLUS", "\+"),
            rule("MINUS", "-"),
            rule("DIV", "/"),
            rule("MUL", "\*"),
            rule("LPAREN", "\("),
            rule("RPAREN", "\)"),
            rule("LBRACK", "{"),
            rule("RBRACK", "}"),
            rule("COLON", ":"),
            rule("SEMICOLON", ";"),
            rule("DOT", "[.]"),
            rule("COMMA", "[,]"),
            rule("EQUAL", "="),
            rule("WHITESPACE", "( )"),
            rule("NEWLINE", "\\n"),
            rule("TAB", "\\t"),
            rule("BEGIN_COMMENT", "/\*"),
            rule("END_COMMENT", "\*/"),
        ]

    @args(
        """oper: int simple_function(int myint) {
    exodus myint;
}

oper: int initus() {
    exodus simple_function(myint=0)
}"""
    )
    def test_scan_simple_program(self):
        self.assert_tokens(
            "OPER",
            "COLON",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "INT",
            "WHITESPACE",
            "ID",
            "RPAREN",
            "WHITESPACE",
            "LBRACK",
            "NEWLINE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "EXODUS",
            "WHITESPACE",
            "ID",
            "SEMICOLON",
            "NEWLINE",
            "RBRACK",
            "NEWLINE",
            "NEWLINE",
            "OPER",
            "COLON",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "INITUS",
            "LPAREN",
            "RPAREN",
            "WHITESPACE",
            "LBRACK",
            "NEWLINE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "EXODUS",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "ID",
            "EQUAL",
            "INT_LITERAL",
            "RPAREN",
            "NEWLINE",
            "RBRACK",
        )

    @args(
        """oper: int add(int a, int b) {
    exodus a + b;
}

oper: int mul(int a, int b) {
    exodus a * b;
}

oper: int initus() {
    exodus add(a=2, b=3) + mul(a=4, b=5)
}"""
    )
    def test_scan_program(self):
        self.assert_tokens(
            "OPER",
            "COLON",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "INT",
            "WHITESPACE",
            "ID",
            "COMMA",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "ID",
            "RPAREN",
            "WHITESPACE",
            "LBRACK",
            "NEWLINE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "EXODUS",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "PLUS",
            "WHITESPACE",
            "ID",
            "SEMICOLON",
            "NEWLINE",
            "RBRACK",
            "NEWLINE",
            "NEWLINE",
            "OPER",
            "COLON",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "INT",
            "WHITESPACE",
            "ID",
            "COMMA",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "ID",
            "RPAREN",
            "WHITESPACE",
            "LBRACK",
            "NEWLINE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "EXODUS",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "MUL",
            "WHITESPACE",
            "ID",
            "SEMICOLON",
            "NEWLINE",
            "RBRACK",
            "NEWLINE",
            "NEWLINE",
            "OPER",
            "COLON",
            "WHITESPACE",
            "INT",
            "WHITESPACE",
            "INITUS",
            "LPAREN",
            "RPAREN",
            "WHITESPACE",
            "LBRACK",
            "NEWLINE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "WHITESPACE",
            "EXODUS",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "ID",
            "EQUAL",
            "INT_LITERAL",
            "COMMA",
            "WHITESPACE",
            "ID",
            "EQUAL",
            "INT_LITERAL",
            "RPAREN",
            "WHITESPACE",
            "PLUS",
            "WHITESPACE",
            "ID",
            "LPAREN",
            "ID",
            "EQUAL",
            "INT_LITERAL",
            "COMMA",
            "WHITESPACE",
            "ID",
            "EQUAL",
            "INT_LITERAL",
            "RPAREN",
            "NEWLINE",
            "RBRACK",
        )


class TestScannerForGrammar(TestScanner):
    def rules(self):
        return [
            rule("FOR", "for"),
            rule("ID", "[a-zA-Z_]+[a-zA-Z_]*"),
        ]

    @args("for fortune format")
    def test_for_grammar(self):
        self.assert_tokens("FOR", "ID", "ID")


class TestScannerIgnoreWhitespace(TestScanner):
    def scanner(self):
        scanner = Scanner(self.configuration())
        scanner.set_handler(self.rules()[1], self.ignore_whitespace)
        return scanner

    def rules(self):
        return [
            rule("ID", "[a-zA-Z_]+[a-zA-Z_]*"),
            rule("WHITESPACE", "( )"),
        ]

    @staticmethod
    def ignore_whitespace(matched: str, rule: Rule) -> None:
        return

    @args("yet another test only ids matchhh")
    def test_ignore_whitespace(self):
        self.assert_tokens("ID", "ID", "ID", "ID", "ID", "ID")


class TestScannerCustomHandler(TestScanner):
    class MyObj:
        def __init__(self, literal, rule) -> None:
            self.literal = literal
            self.rule = rule

    def scanner(self):
        scanner = Scanner(self.configuration())
        {scanner.set_handler(rule, self.handler) for rule in self.configuration().rules}
        return scanner

    def rules(self):
        return [
            rule("IF", "if"),
            rule("WHEN", "when"),
            rule("ID", "[a-zA-Z_]*"),
            rule("WHITESPACE", "( )"),
        ]

    @staticmethod
    def handler(matched, rule):
        return TestScannerCustomHandler.MyObj(matched, rule)

    def assert_objs(self, *matched):
        self.assertSequenceEqual(
            list(map(lambda o: o.rule.name, self.result())), matched
        )

    @args("if yoyo when then is myvar")
    def test_return_custom_objs(self):
        self.assert_objs(
            "IF",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "WHEN",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "ID",
            "WHITESPACE",
            "ID",
        )


class TestKeywordsBeforeIdentifiers(TestScanner):
    def rules(self):
        return [
            rule("EXODUS", "exodus"),
            rule("INT", "int"),
            rule("ID", "[a-zA-Z_][a-zA-Z0-9_]*"),
            rule("WHITESPACE", " "),
        ]

    @args("exodus")
    def test_keyword_alone(self):
        self.assert_tokens("EXODUS")

    @args("exodusx")
    def test_keyword_followed_by_letter_is_identifier(self):
        self.assert_tokens("ID")
        self.assert_literals("exodusx")

    @args("exodus_value")
    def test_keyword_followed_by_underscore_is_identifier(self):
        self.assert_tokens("ID")

    @args("exodus1")
    def test_keyword_followed_by_digit_is_identifier(self):
        self.assert_tokens("ID")

    @args("intus")
    def test_keyword_prefix_of_longer_word(self):
        self.assert_tokens("ID")
        self.assert_literals("intus")

    @args("in")
    def test_proper_prefix_of_keyword_is_identifier(self):
        self.assert_tokens("ID")

    @args("x_int")
    def test_keyword_as_suffix_of_identifier(self):
        self.assert_tokens("ID")

    @args("int intx int")
    def test_keyword_identifier_keyword(self):
        self.assert_tokens("INT", "WHITESPACE", "ID", "WHITESPACE", "INT")
        self.assert_literals("int", " ", "intx", " ", "int")


class TestRuleOrderBreaksTies(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("INT", "int"),
        ]

    @args("int")
    def test_earlier_rule_wins_equal_length(self):
        self.assert_tokens("ID")


class TestNumberLiterals(TestScanner):
    def rules(self):
        return [
            rule("DOUBLE_LITERAL", r"[0-9]+\.[0-9]+"),
            rule("INT_LITERAL", "[0-9]+"),
            rule("DOT", r"\."),
            rule("ID", "[a-z]+"),
        ]

    @args("1.5")
    def test_double(self):
        self.assert_tokens("DOUBLE_LITERAL")
        self.assert_literals("1.5")

    @args("12.750")
    def test_multi_digit_double(self):
        self.assert_tokens("DOUBLE_LITERAL")

    @args("42")
    def test_int(self):
        self.assert_tokens("INT_LITERAL")
        self.assert_literals("42")

    @args("1.")
    def test_int_then_dot_needs_backtracking(self):
        self.assert_tokens("INT_LITERAL", "DOT")

    @args("1.x")
    def test_int_dot_identifier(self):
        self.assert_tokens("INT_LITERAL", "DOT", "ID")

    @args("a.b")
    def test_member_access(self):
        self.assert_tokens("ID", "DOT", "ID")

    @args("1.5.2")
    def test_double_then_dot_then_int(self):
        self.assert_tokens("DOUBLE_LITERAL", "DOT", "INT_LITERAL")


class TestOperators(TestScanner):
    def rules(self):
        return [
            rule("BEGIN_COMMENT", r"/\*"),
            rule("END_COMMENT", r"\*/"),
            rule("EQEQ", "=="),
            rule("ARROW", "->"),
            rule("DIV", "/"),
            rule("MUL", r"\*"),
            rule("EQUAL", "="),
            rule("MINUS", "-"),
            rule("GT", ">"),
            rule("ID", "[a-z]+"),
            rule("WHITESPACE", " "),
        ]

    @args("/*")
    def test_begin_comment(self):
        self.assert_tokens("BEGIN_COMMENT")

    @args("*/")
    def test_end_comment(self):
        self.assert_tokens("END_COMMENT")

    @args("/ *")
    def test_div_space_mul(self):
        self.assert_tokens("DIV", "WHITESPACE", "MUL")

    @args("a/*b*/c")
    def test_comment_markers_without_spaces(self):
        self.assert_tokens("ID", "BEGIN_COMMENT", "ID", "END_COMMENT", "ID")

    @args("==")
    def test_double_equal(self):
        self.assert_tokens("EQEQ")

    @args("===")
    def test_triple_equal_is_eqeq_then_equal(self):
        self.assert_tokens("EQEQ", "EQUAL")

    @args("a=b")
    def test_single_equal(self):
        self.assert_tokens("ID", "EQUAL", "ID")

    @args("a->b")
    def test_arrow(self):
        self.assert_tokens("ID", "ARROW", "ID")

    @args("a - > b")
    def test_minus_and_gt_separated(self):
        self.assert_tokens(
            "ID", "WHITESPACE", "MINUS", "WHITESPACE", "GT", "WHITESPACE", "ID"
        )


class TestWhitespace(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("WHITESPACE", " "),
            rule("NEWLINE", "\n"),
            rule("TAB", "\t"),
        ]

    @args("  x")
    def test_leading_whitespace(self):
        self.assert_tokens("WHITESPACE", "WHITESPACE", "ID")

    @args("x  ")
    def test_trailing_whitespace(self):
        self.assert_tokens("ID", "WHITESPACE", "WHITESPACE")

    @args("a\n\tb\n")
    def test_newline_and_tab(self):
        self.assert_tokens("ID", "NEWLINE", "TAB", "ID", "NEWLINE")

    @args("\n")
    def test_only_newline(self):
        self.assert_tokens("NEWLINE")


class TestGreedyWhitespaceRule(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("WHITESPACE", "[ \t]+"),
        ]

    @args("a   \t b")
    def test_whitespace_run_is_one_token(self):
        self.assert_tokens("ID", "WHITESPACE", "ID")
        self.assert_literals("a", "   \t ", "b")


class TestEdgeInputs(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("WHITESPACE", " "),
        ]

    @args("")
    def test_empty_text(self):
        self.assert_tokens()
        self.assert_unmatched()

    @args("x")
    def test_single_character_token(self):
        self.assert_tokens("ID")
        self.assert_literals("x")

    @args("@")
    def test_single_unmatched_character(self):
        self.assert_tokens()
        self.assert_unmatched("@")

    @args("abcdefghijklmnopqrstuvwxyz")
    def test_long_single_token(self):
        self.assert_literals("abcdefghijklmnopqrstuvwxyz")


class TestLongInput(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("INT", "[0-9]+"),
            rule("WHITESPACE", " "),
        ]

    @args("abc 123 " * 5000)
    def test_token_count(self):
        self.assertEqual(len(self.result()), 20000)


class TestUnmatched(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]+"),
            rule("WHITESPACE", " "),
        ]

    @args("@abc")
    def test_leading(self):
        self.assert_tokens("ID")
        self.assert_unmatched("@")

    @args("abc@")
    def test_trailing(self):
        self.assert_tokens("ID")
        self.assert_unmatched("@")

    @args("ab@cd")
    def test_in_the_middle(self):
        self.assert_tokens("ID", "ID")
        self.assert_literals("ab", "cd")
        self.assert_unmatched("@")

    @args("@@@")
    def test_only_unmatched(self):
        self.assert_tokens()
        self.assertEqual("".join(self.unmatched), "@@@")

    @args("a @ b # c")
    def test_several_separate_runs(self):
        self.assert_tokens(
            "ID", "WHITESPACE", "WHITESPACE", "ID", "WHITESPACE", "WHITESPACE", "ID"
        )
        self.assert_unmatched("@", "#")


class TestRuleThatCanMatchEmptyString(TestScanner):
    def rules(self):
        return [
            rule("ID", "[a-z]*"),
            rule("INT", "[0-9]+"),
        ]

    @args("12")
    def test_no_empty_tokens(self):
        self.assert_tokens("INT")
        self.assert_literals("12")

    @args("@")
    def test_no_empty_token_for_unmatched(self):
        self.assert_tokens()
        self.assert_unmatched("@")


class TestRoundTrip(TestCase):
    RULES = [
        rule("FOR", "for"),
        rule("ID", "[a-zA-Z_][a-zA-Z0-9_]*"),
        rule("INT", "[0-9]+"),
        rule("OP", r"[+\-*/=]"),
        rule("WHITESPACE", "[ \t\n]+"),
    ]

    def subject(self, text):
        pieces = []
        scanner = Scanner(Configuration(self.RULES))
        scanner.set_unmatched_handler(pieces.append)
        for r in self.RULES:
            scanner.set_handler(r, lambda literal, _rule: pieces.append(literal))
        list(scanner.scan(text))
        return "".join(pieces)

    def assert_round_trip(self):
        self.assertResult(self.subjectKwargs()["text"])

    @args(text="for x = 1 + 2")
    def test_simple(self):
        self.assert_round_trip()

    @args(text="fortune @ 12 $$ y")
    def test_with_junk(self):
        self.assert_round_trip()

    @args(text="  a\n\tb  ")
    def test_with_layout(self):
        self.assert_round_trip()

    @args(text="x?")
    def test_trailing_junk(self):
        self.assert_round_trip()


class TestUnicodeIdentifiers(TestScanner):
    def rules(self):
        return [
            rule("ID", r"[^\W\d]\w*"),
            rule("INT", "[0-9]+"),
            rule("EQUAL", "="),
            rule("WHITESPACE", " "),
        ]

    @args("λόγος = 1")
    def test_greek_identifier(self):
        self.assert_tokens("ID", "WHITESPACE", "EQUAL", "WHITESPACE", "INT")
        self.assert_literals("λόγος", " ", "=", " ", "1")

    @args("ἀρχή")
    def test_polytonic_identifier(self):
        self.assert_literals("ἀρχή")

    @args("café")
    def test_latin_with_accent(self):
        self.assert_literals("café")


class TestHandlers(TestCase):
    def test_handler_receives_literal_and_rule(self):
        number = rule("INT", "[0-9]+")
        received = []
        scanner = Scanner(Configuration([number, rule("WS", " ")]))
        scanner.set_handler(number, lambda lit, r: received.append((lit, r)))
        list(scanner.scan("12 345"))
        self.assertEqual(received, [("12", number), ("345", number)])

    def test_handler_return_value_is_yielded(self):
        number = rule("INT", "[0-9]+")
        scanner = Scanner(Configuration([number]))
        scanner.set_handler(number, lambda lit, _r: int(lit))
        self.assertEqual(list(scanner.scan("42")), [42])

    def test_handler_only_affects_its_rule(self):
        number = rule("INT", "[0-9]+")
        word = rule("ID", "[a-z]+")
        scanner = Scanner(Configuration([number, word]))
        scanner.set_handler(number, lambda lit, _r: None)
        self.assertEqual([t.name for t in scanner.scan("ab12cd")], ["ID", "ID"])

    def test_rules_with_same_name_and_different_regex_keep_separate_handlers(self):
        lower = rule("WORD", "[a-z]+")
        upper = rule("WORD", "[A-Z]+")
        scanner = Scanner(Configuration([lower, upper]))
        scanner.set_handler(lower, lambda lit, _r: ("lower", lit))
        scanner.set_handler(upper, lambda lit, _r: ("upper", lit))
        self.assertEqual(list(scanner.scan("abCD")), [("lower", "ab"), ("upper", "CD")])


class TestScannerReuse(TestCase):
    def scanner(self):
        return Scanner(Configuration([rule("ID", "[a-z]+"), rule("WS", " ")]))

    @staticmethod
    def literals(tokens):
        return [t.literal for t in tokens]

    def test_scan_twice_gives_same_result(self):
        scanner = self.scanner()
        first = self.literals(scanner.scan("aa bb"))
        second = self.literals(scanner.scan("aa bb"))
        self.assertEqual(first, second)

    def test_scan_after_partially_consumed_scan(self):
        scanner = self.scanner()
        next(scanner.scan("aa bb cc"))
        self.assertEqual(self.literals(scanner.scan("dd ee")), ["dd", " ", "ee"])

    def test_interleaved_scans_are_independent(self):
        scanner = self.scanner()
        g1, g2 = scanner.scan("aa bb"), scanner.scan("cc dd")
        out1, out2 = [], []
        for _ in range(3):
            out1.append(next(g1).literal)
            out2.append(next(g2).literal)
        self.assertEqual(out1, ["aa", " ", "bb"])
        self.assertEqual(out2, ["cc", " ", "dd"])


class TestInvalidPattern(TestCase):
    def test_scanning_with_invalid_pattern_raises(self):
        scanner = Scanner(Configuration([rule("BAD", "(")]))
        with self.assertRaises(RegexPatternError):
            list(scanner.scan("x"))
