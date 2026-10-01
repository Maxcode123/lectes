from unittest_extensions import args, TestCase

from lectes.config.models import Rule, Configuration
from lectes.engine.models import Regex
from lectes.scanner.scanner import Scanner


def rule(name, regex):
    return Rule(name=name, regex=Regex(regex))


class TestProgram(TestCase):
    """
    Lexes whole programs and compares (name, literal) pairs. Tokens of rules
    named in SKIP (whitespace, comments) are dropped from the result.
    """

    SKIP: tuple[str, ...] = ()

    def rules(self):
        return []

    def subject(self, text):
        self.unmatched = []
        rules = self.rules()
        scanner = Scanner(Configuration(rules))
        scanner.set_unmatched_handler(self.unmatched.append)
        for r in rules:
            if r.name in self.SKIP:
                scanner.set_handler(r, lambda _literal, _rule: None)
        return [(t.name, t.literal) for t in scanner.scan(text)]

    def assert_lexemes(self, *lexemes):
        self.assertResult(list(lexemes))
        self.assertEqual(self.unmatched, [])
        self.assert_round_trip()

    def assert_round_trip(self):
        # Without skipping, the token literals must reconstruct the source.
        text = self.subjectKwargs()["text"]
        tokens = Scanner(Configuration(self.rules())).scan(text)
        self.assertEqual("".join(t.literal for t in tokens), text)


class TestCLikeProgram(TestProgram):
    SKIP = ("WHITESPACE", "LINE_COMMENT", "BLOCK_COMMENT")

    def rules(self):
        return [
            rule("IF", "if"),
            rule("ELSE", "else"),
            rule("WHILE", "while"),
            rule("FOR", "for"),
            rule("RETURN", "return"),
            rule("INT", "int"),
            rule("CHAR", "char"),
            rule("ID", "[A-Za-z_][A-Za-z0-9_]*"),
            rule("HEX", "0[xX][0-9a-fA-F]+"),
            rule("FLOAT", r"[0-9]+\.[0-9]+"),
            rule("INT_LITERAL", "[0-9]+"),
            rule("STRING", r'"(\\.|[^"\\\n])*"'),
            rule("CHAR_LITERAL", r"'(\\.|[^'\\\n])'"),
            rule("LINE_COMMENT", r"//[^\n]*"),
            rule("BLOCK_COMMENT", r"/\*[\s\S]*?\*/"),
            rule("INCR", r"\+\+"),
            rule("PLUS_ASSIGN", r"\+="),
            rule("PLUS", r"\+"),
            rule("MINUS", "-"),
            rule("STAR", r"\*"),
            rule("SLASH", "/"),
            rule("PERCENT", "%"),
            rule("LE", "<="),
            rule("LT", "<"),
            rule("EQ", "=="),
            rule("NE", "!="),
            rule("NOT", "!"),
            rule("ASSIGN", "="),
            rule("AND", "&&"),
            rule("OR", r"\|\|"),
            rule("LPAREN", r"\("),
            rule("RPAREN", r"\)"),
            rule("LBRACE", "{"),
            rule("RBRACE", "}"),
            rule("LBRACKET", r"\["),
            rule("RBRACKET", r"\]"),
            rule("SEMICOLON", ";"),
            rule("COMMA", ","),
            rule("WHITESPACE", r"[ \t\n]+"),
        ]

    @args(
        text="""/* Computes n! recursively. */
int fact(int n) {
    if (n <= 1) return 1; // base case
    return n * fact(n - 1);
}"""
    )
    def test_recursive_function(self):
        self.assert_lexemes(
            ("INT", "int"), ("ID", "fact"), ("LPAREN", "("), ("INT", "int"),
            ("ID", "n"), ("RPAREN", ")"), ("LBRACE", "{"),
            ("IF", "if"), ("LPAREN", "("), ("ID", "n"), ("LE", "<="),
            ("INT_LITERAL", "1"), ("RPAREN", ")"), ("RETURN", "return"),
            ("INT_LITERAL", "1"), ("SEMICOLON", ";"),
            ("RETURN", "return"), ("ID", "n"), ("STAR", "*"), ("ID", "fact"),
            ("LPAREN", "("), ("ID", "n"), ("MINUS", "-"), ("INT_LITERAL", "1"),
            ("RPAREN", ")"), ("SEMICOLON", ";"),
            ("RBRACE", "}"),
        )  # fmt: skip

    @args(
        text=r"""int main() {
    int total = 0x1F;
    for (int i = 0; i < 10 && total != 0; i++) {
        total += i % 3;
    }
    printf("total: \"%d\"\n", total);
    char c = '\'';
    return total * 3.14;
}"""
    )
    def test_main_with_loop_and_literals(self):
        self.assert_lexemes(
            ("INT", "int"), ("ID", "main"), ("LPAREN", "("), ("RPAREN", ")"),
            ("LBRACE", "{"),
            ("INT", "int"), ("ID", "total"), ("ASSIGN", "="), ("HEX", "0x1F"),
            ("SEMICOLON", ";"),
            ("FOR", "for"), ("LPAREN", "("), ("INT", "int"), ("ID", "i"),
            ("ASSIGN", "="), ("INT_LITERAL", "0"), ("SEMICOLON", ";"),
            ("ID", "i"), ("LT", "<"), ("INT_LITERAL", "10"), ("AND", "&&"),
            ("ID", "total"), ("NE", "!="), ("INT_LITERAL", "0"),
            ("SEMICOLON", ";"), ("ID", "i"), ("INCR", "++"), ("RPAREN", ")"),
            ("LBRACE", "{"),
            ("ID", "total"), ("PLUS_ASSIGN", "+="), ("ID", "i"),
            ("PERCENT", "%"), ("INT_LITERAL", "3"), ("SEMICOLON", ";"),
            ("RBRACE", "}"),
            ("ID", "printf"), ("LPAREN", "("),
            ("STRING", r'"total: \"%d\"\n"'), ("COMMA", ","), ("ID", "total"),
            ("RPAREN", ")"), ("SEMICOLON", ";"),
            ("CHAR", "char"), ("ID", "c"), ("ASSIGN", "="),
            ("CHAR_LITERAL", r"'\''"), ("SEMICOLON", ";"),
            ("RETURN", "return"), ("ID", "total"), ("STAR", "*"),
            ("FLOAT", "3.14"), ("SEMICOLON", ";"),
            ("RBRACE", "}"),
        )  # fmt: skip

    @args(text='x = "// not a comment";')
    def test_comment_marker_inside_string(self):
        self.assert_lexemes(
            ("ID", "x"),
            ("ASSIGN", "="),
            ("STRING", '"// not a comment"'),
            ("SEMICOLON", ";"),
        )

    @args(text="a/b/*c*/d")
    def test_division_and_block_comment(self):
        self.assert_lexemes(("ID", "a"), ("SLASH", "/"), ("ID", "b"), ("ID", "d"))

    @args(text='"abc')
    def test_unterminated_string(self):
        self.assertResult([("ID", "abc")])
        self.assertEqual(self.unmatched, ['"'])


class TestPythonLikeProgram(TestProgram):
    # Indentation is skipped like any other whitespace: producing INDENT and
    # DEDENT tokens needs state the scanner does not keep.
    SKIP = ("WHITESPACE", "COMMENT")

    def rules(self):
        return [
            rule("DEF", "def"),
            rule("RETURN", "return"),
            rule("IF", "if"),
            rule("ELIF", "elif"),
            rule("ELSE", "else"),
            rule("FOR", "for"),
            rule("IN", "in"),
            rule("WHILE", "while"),
            rule("NOT", "not"),
            rule("AND", "and"),
            rule("OR", "or"),
            rule("TRUE", "True"),
            rule("FALSE", "False"),
            rule("NONE", "None"),
            rule("ID", "[A-Za-z_][A-Za-z0-9_]*"),
            rule("FLOAT", r"[0-9]+\.[0-9]+"),
            rule("INT", "[0-9]+"),
            rule("STRING", r'"(\\.|[^"\\\n])*"' + "|" + r"'(\\.|[^'\\\n])*'"),
            rule("COMMENT", r"#[^\n]*"),
            rule("POW", r"\*\*"),
            rule("FLOORDIV", "//"),
            rule("ARROW", "->"),
            rule("EQ", "=="),
            rule("NE", "!="),
            rule("LE", "<="),
            rule("GE", ">="),
            rule("LT", "<"),
            rule("GT", ">"),
            rule("ASSIGN", "="),
            rule("PLUS", r"\+"),
            rule("MINUS", "-"),
            rule("STAR", r"\*"),
            rule("SLASH", "/"),
            rule("PERCENT", "%"),
            rule("COLON", ":"),
            rule("COMMA", ","),
            rule("DOT", r"\."),
            rule("AT", "@"),
            rule("LPAREN", r"\("),
            rule("RPAREN", r"\)"),
            rule("LBRACKET", r"\["),
            rule("RBRACKET", r"\]"),
            rule("NEWLINE", r"\n"),
            rule("WHITESPACE", r"[ \t]+"),
        ]

    @args(
        text="""for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print('Fizz')
    else:
        print(i)  # neither"""
    )
    def test_fizzbuzz(self):
        self.assert_lexemes(
            ("FOR", "for"), ("ID", "i"), ("IN", "in"), ("ID", "range"),
            ("LPAREN", "("), ("INT", "1"), ("COMMA", ","), ("INT", "101"),
            ("RPAREN", ")"), ("COLON", ":"), ("NEWLINE", "\n"),
            ("IF", "if"), ("ID", "i"), ("PERCENT", "%"), ("INT", "15"),
            ("EQ", "=="), ("INT", "0"), ("COLON", ":"), ("NEWLINE", "\n"),
            ("ID", "print"), ("LPAREN", "("), ("STRING", '"FizzBuzz"'),
            ("RPAREN", ")"), ("NEWLINE", "\n"),
            ("ELIF", "elif"), ("ID", "i"), ("PERCENT", "%"), ("INT", "3"),
            ("EQ", "=="), ("INT", "0"), ("COLON", ":"), ("NEWLINE", "\n"),
            ("ID", "print"), ("LPAREN", "("), ("STRING", "'Fizz'"),
            ("RPAREN", ")"), ("NEWLINE", "\n"),
            ("ELSE", "else"), ("COLON", ":"), ("NEWLINE", "\n"),
            ("ID", "print"), ("LPAREN", "("), ("ID", "i"), ("RPAREN", ")"),
        )  # fmt: skip

    @args(
        text="""@cache
def area(r: float) -> float:
    half = r // 2
    return 3.14159 * r ** 2 if r >= 0 else None"""
    )
    def test_decorated_typed_function(self):
        self.assert_lexemes(
            ("AT", "@"), ("ID", "cache"), ("NEWLINE", "\n"),
            ("DEF", "def"), ("ID", "area"), ("LPAREN", "("), ("ID", "r"),
            ("COLON", ":"), ("ID", "float"), ("RPAREN", ")"), ("ARROW", "->"),
            ("ID", "float"), ("COLON", ":"), ("NEWLINE", "\n"),
            ("ID", "half"), ("ASSIGN", "="), ("ID", "r"), ("FLOORDIV", "//"),
            ("INT", "2"), ("NEWLINE", "\n"),
            ("RETURN", "return"), ("FLOAT", "3.14159"), ("STAR", "*"),
            ("ID", "r"), ("POW", "**"), ("INT", "2"), ("IF", "if"), ("ID", "r"),
            ("GE", ">="), ("INT", "0"), ("ELSE", "else"), ("NONE", "None"),
        )  # fmt: skip

    @args(text="in int index not notable or order")
    def test_keywords_as_identifier_prefixes(self):
        self.assert_lexemes(
            ("IN", "in"),
            ("ID", "int"),
            ("ID", "index"),
            ("NOT", "not"),
            ("ID", "notable"),
            ("OR", "or"),
            ("ID", "order"),
        )

    @args(text="s = '# not a comment'  # a comment")
    def test_comment_marker_inside_string(self):
        self.assert_lexemes(
            ("ID", "s"), ("ASSIGN", "="), ("STRING", "'# not a comment'")
        )


class TestJSONDocument(TestProgram):
    SKIP = ("WHITESPACE",)

    def rules(self):
        return [
            rule("LBRACE", "{"),
            rule("RBRACE", "}"),
            rule("LBRACKET", r"\["),
            rule("RBRACKET", r"\]"),
            rule("COLON", ":"),
            rule("COMMA", ","),
            rule("TRUE", "true"),
            rule("FALSE", "false"),
            rule("NULL", "null"),
            rule("STRING", r'"(\\.|[^"\\])*"'),
            rule("NUMBER", r"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?"),
            rule("WHITESPACE", r"[ \t\n\r]+"),
        ]

    @args(
        text=r"""{
    "name": "lectes",
    "version": 0.2,
    "tags": ["lexer", "scanner"],
    "stable": false,
    "license": null,
    "path": "C:\\Users\\me \"home\" caf\u00e9",
    "deps": {"python": true, "count": 2}
}"""
    )
    def test_nested_document(self):
        self.assert_lexemes(
            ("LBRACE", "{"),
            ("STRING", '"name"'), ("COLON", ":"), ("STRING", '"lectes"'),
            ("COMMA", ","),
            ("STRING", '"version"'), ("COLON", ":"), ("NUMBER", "0.2"),
            ("COMMA", ","),
            ("STRING", '"tags"'), ("COLON", ":"), ("LBRACKET", "["),
            ("STRING", '"lexer"'), ("COMMA", ","), ("STRING", '"scanner"'),
            ("RBRACKET", "]"), ("COMMA", ","),
            ("STRING", '"stable"'), ("COLON", ":"), ("FALSE", "false"),
            ("COMMA", ","),
            ("STRING", '"license"'), ("COLON", ":"), ("NULL", "null"),
            ("COMMA", ","),
            ("STRING", '"path"'), ("COLON", ":"),
            ("STRING", r'"C:\\Users\\me \"home\" caf\u00e9"'), ("COMMA", ","),
            ("STRING", '"deps"'), ("COLON", ":"), ("LBRACE", "{"),
            ("STRING", '"python"'), ("COLON", ":"), ("TRUE", "true"),
            ("COMMA", ","), ("STRING", '"count"'), ("COLON", ":"),
            ("NUMBER", "2"), ("RBRACE", "}"),
            ("RBRACE", "}"),
        )  # fmt: skip

    @args(text="[0, -0.5e10, 1E+2, 42]")
    def test_number_formats(self):
        self.assert_lexemes(
            ("LBRACKET", "["), ("NUMBER", "0"), ("COMMA", ","),
            ("NUMBER", "-0.5e10"), ("COMMA", ","), ("NUMBER", "1E+2"),
            ("COMMA", ","), ("NUMBER", "42"), ("RBRACKET", "]"),
        )  # fmt: skip

    @args(text="01")
    def test_leading_zero_splits_number(self):
        self.assert_lexemes(("NUMBER", "0"), ("NUMBER", "1"))

    @args(text="trueish")
    def test_literal_followed_by_junk(self):
        self.assertResult([("TRUE", "true")])
        self.assertEqual(self.unmatched, ["ish"])


class TestLispProgram(TestProgram):
    SKIP = ("WHITESPACE", "COMMENT")

    def rules(self):
        return [
            rule("LPAREN", r"\("),
            rule("RPAREN", r"\)"),
            rule("QUOTE", "'"),
            rule("BOOLEAN", "#t|#f"),
            rule("STRING", r'"(\\.|[^"\\])*"'),
            rule("NUMBER", r"-?[0-9]+(\.[0-9]+)?"),
            rule(
                "SYMBOL",
                r"[a-zA-Z!$%&*/:<=>?^_~+\-][a-zA-Z0-9!$%&*/:<=>?^_~+\-.]*",
            ),
            rule("COMMENT", r";[^\n]*"),
            rule("WHITESPACE", r"[ \t\n]+"),
        ]

    @args(
        text="""; Factorial, the classic way.
(define (fact n)
  (if (= n 0)
      1
      (* n (fact (- n 1)))))"""
    )
    def test_factorial(self):
        self.assert_lexemes(
            ("LPAREN", "("), ("SYMBOL", "define"), ("LPAREN", "("),
            ("SYMBOL", "fact"), ("SYMBOL", "n"), ("RPAREN", ")"),
            ("LPAREN", "("), ("SYMBOL", "if"), ("LPAREN", "("), ("SYMBOL", "="),
            ("SYMBOL", "n"), ("NUMBER", "0"), ("RPAREN", ")"),
            ("NUMBER", "1"),
            ("LPAREN", "("), ("SYMBOL", "*"), ("SYMBOL", "n"), ("LPAREN", "("),
            ("SYMBOL", "fact"), ("LPAREN", "("), ("SYMBOL", "-"),
            ("SYMBOL", "n"), ("NUMBER", "1"), ("RPAREN", ")"), ("RPAREN", ")"),
            ("RPAREN", ")"), ("RPAREN", ")"), ("RPAREN", ")"),
        )  # fmt: skip

    @args(
        text="""(define (vectors lst)
  (if (null? lst)
      #f
      (map list->vector '((1 2) (3.5 -4)) "done")))"""
    )
    def test_quoted_list_and_special_symbols(self):
        self.assert_lexemes(
            ("LPAREN", "("), ("SYMBOL", "define"), ("LPAREN", "("),
            ("SYMBOL", "vectors"), ("SYMBOL", "lst"), ("RPAREN", ")"),
            ("LPAREN", "("), ("SYMBOL", "if"), ("LPAREN", "("),
            ("SYMBOL", "null?"), ("SYMBOL", "lst"), ("RPAREN", ")"),
            ("BOOLEAN", "#f"),
            ("LPAREN", "("), ("SYMBOL", "map"), ("SYMBOL", "list->vector"),
            ("QUOTE", "'"), ("LPAREN", "("), ("LPAREN", "("), ("NUMBER", "1"),
            ("NUMBER", "2"), ("RPAREN", ")"), ("LPAREN", "("),
            ("NUMBER", "3.5"), ("NUMBER", "-4"), ("RPAREN", ")"),
            ("RPAREN", ")"), ("STRING", '"done"'), ("RPAREN", ")"),
            ("RPAREN", ")"), ("RPAREN", ")"),
        )  # fmt: skip

    @args(text="- -5 -x")
    def test_minus_number_and_symbol(self):
        self.assert_lexemes(("SYMBOL", "-"), ("NUMBER", "-5"), ("SYMBOL", "-x"))
