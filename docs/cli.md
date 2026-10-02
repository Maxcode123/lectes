# Command line

lectes comes with a `lectes` command that scans a file, or stdin, with a grammar
file and prints the tokens. It's handy for developing a grammar and for feeding
tokens to other tools.

```sh
lectes GRAMMAR [INPUT]
```

Running `lectes` with no arguments prints the help, as `lectes --help` does.
See [Installation](installation.md) for how to put `lectes` on your `PATH`.

## Grammar files

A grammar file has one rule per line: a name, whitespace, then the regex, which
is the rest of the line. Blank lines and lines starting with `#` are ignored.
Rules are tried in order, and the longest match wins, so the order only
matters when two rules match the same text.

By convention, grammar files use the `.lectes` extension.

```text
# arithmetic.lectes
INT     [0-9]+
ID      [a-zA-Z_][a-zA-Z0-9_]*
PLUS    \+
WS      \s+
```

Rule names start with a letter or underscore and contain only letters, digits
and underscores. Regexes use Python's [`re`](https://docs.python.org/3/library/re.html)
syntax and are written as-is, with no quoting or escaping beyond what the regex
itself needs.

The same format can be loaded from Python with `Configuration.from_text`; see
[Usage](usage.md#defining-the-rules-in-a-grammar).

## Output

By default each token is printed on its own line, as its `line:column`, its
rule name and its literal:

```console
$ echo '12 + x' | lectes arithmetic.lectes
1:1     INT   '12'
1:3     WS    ' '
1:4     PLUS  '+'
1:5     WS    ' '
1:6     ID    'x'
1:7     WS    '\n'
```

Literals are shown with Python's `repr`, so whitespace and other special
characters are visible.

With `--format json`, each token is printed as a JSON object on its own line
([JSON Lines](https://jsonlines.org/)), ready for `jq` or another program:

```console
$ echo '12 + x' | lectes arithmetic.lectes --format json
{"name": "INT", "literal": "12", "offset": 0, "line": 1, "column": 1}
{"name": "WS", "literal": " ", "offset": 2, "line": 1, "column": 3}
...
```

`offset` is 0-based and counts characters; `line` and `column` are 1-based.

## Unmatched text

By default, scanning stops at the first text that no rule matches. The tokens
before it have already been printed, and the unmatched text is reported on
stderr:

```console
$ echo '12 @ x' | lectes arithmetic.lectes
1:1     INT   '12'
1:3     WS    ' '
<stdin>:1:4: unmatched '@'
```

With `--ignore-unmatched`, every run of unmatched text is reported on stderr
and scanning continues. Unmatched text is always reported on stderr, in both
output formats, so stdout only ever holds tokens.

## Grammar errors and warnings

Problems in the grammar file are reported on stderr with their line number,
in a form most editors can jump to. Every error is reported, not just the
first one:

```console
$ lectes broken.lectes input.txt
broken.lectes:1: error: invalid rule name '9X'
broken.lectes:3: error: rule 'ID' has no pattern
```

Warnings point out rules that are valid but probably not what you meant, such
as a rule that can match the empty string. They're reported the same way, but
scanning goes ahead.

Use `--check` to validate a grammar without scanning anything.

## Options

| Option | Description |
|---|---|
| `INPUT` | File to scan. Reads stdin when omitted or `-`. |
| `--format {text,json}` | Output format; `text` by default. |
| `--ignore-unmatched` | Report unmatched text on stderr and keep scanning. |
| `--encoding ENCODING` | Encoding of the input; `utf-8` by default. Grammar files are always UTF-8. |
| `--check` | Only validate the grammar. |
| `--debug` | Print the scanner's debug events to stderr. |
| `--version` | Print the version and exit. |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. With `--ignore-unmatched`, unmatched text doesn't change this. |
| `1` | The input has text that no rule matches. |
| `2` | A usage error, an invalid grammar, or a file that can't be read or decoded. |
