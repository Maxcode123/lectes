"""
Parser for the grammar text format.

One rule per line: a name, whitespace, then the regex (the rest of the line,
with trailing whitespace stripped). Blank lines and lines starting with `#` are
ignored.
"""

import re
from dataclasses import dataclass, field

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class Grammar:
    rules: list[tuple[str, str]] = field(default_factory=list)
    errors: list[tuple[int | None, str]] = field(default_factory=list)
    warnings: list[tuple[int, str]] = field(default_factory=list)


def parse(text: str) -> Grammar:
    """
    Parse grammar text, reporting every problem rather than stopping at the
    first one.
    """
    grammar = Grammar()
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    for number, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        name, *rest = stripped.split(maxsplit=1)
        pattern = rest[0] if rest else ""

        if not _NAME.fullmatch(name):
            grammar.errors.append((number, f"invalid rule name {name!r}"))
            continue

        if not pattern:
            grammar.errors.append((number, f"rule {name!r} has no pattern"))
            continue

        try:
            compiled = re.compile(pattern)
        except re.error as e:
            position = "" if e.pos is None else f" at position {e.pos}"
            grammar.errors.append((number, f"rule {name!r}: {e.msg}{position}"))
            continue
        except (RecursionError, OverflowError, ValueError) as e:
            grammar.errors.append((number, f"rule {name!r}: {e}"))
            continue

        if compiled.fullmatch(""):
            grammar.warnings.append(
                (
                    number,
                    f"rule {name!r} can match the empty string; "
                    "empty matches are ignored",
                )
            )

        grammar.rules.append((name, pattern))

    if not grammar.rules and not grammar.errors:
        grammar.errors.append((None, "grammar has no rules"))

    return grammar
