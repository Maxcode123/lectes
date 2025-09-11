from unittest_extensions import args, TestCase

from lectes.config.models import Rule, Configuration
from lectes.engine.models import Regex
from lectes.scanner.scanner import Scanner


def rule(name, regex):
    return Rule(name=name, regex=Regex(regex))


class TestScanner(TestCase):
    def subject(self, text):
        return list(self.scanner().scan(text))

    def scanner(self):
        return Scanner(self.configuration())

    def configuration(self):
        return Configuration(self.rules())

    def assert_tokens(self, *tokens):
        self.assertSequenceEqual(list(map(lambda t: t.name, self.result())), tokens)


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
