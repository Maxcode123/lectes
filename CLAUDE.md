# lectes

A simple Python scanner (lexer) generator. You give it named regex rules, and it
yields tokens. It's a library plus a `lectes` CLI, published on PyPI. Docs are at
https://maximosnikiforakis.gr/lectes/.

## Commands

Use uv for everything. The system `python3` doesn't work here, because pyenv
can't find the 3.13 that `.python-version` asks for, so always go through
`uv run python …`.

```sh
make test          # whole unit suite (unittest discover)
make lint          # ruff check (tests are excluded)
make type-check    # ty
make format        # ruff format
uv run python -m unittest src.lectes.tests.unit.test_cli   # one module
uv run lectes --help                                       # try the CLI
uv run mkdocs build --strict -d <scratch dir>              # check the docs
```

Before every commit, run `make test`, `make lint` and `make type-check`, and
make sure `uv run ruff format --check src` is clean.

## Architecture

All code lives in `src/lectes/`:

- `config/`
  - `models.py`: `Rule` (a name plus a `Regex`), and `Configuration` with
    `from_text()`.
  - `grammar.py`: the grammar-text parser. It has no lectes imports and
    collects every error, not just the first.
  - `errors.py`: `GrammarError` (`.problems` is a list of `(line, message)`) and
    `GrammarWarning` (`.line`, `.message`).
- `engine/models.py`: `Regex`, which compiles lazily. `match_prefix` is an
  anchored match.
- `scanner/scanner.py`: `Scanner.scan()` is a generator:
  - The longest match wins, and a tie goes to the earlier rule.
  - Empty matches never produce tokens.
  - Each run of unmatched text is reported once, as `UnmatchedText`. It raises
    `UnmatchedTextError` unless `ignore_unmatched=True` or a handler is set.
- `scanner/models.py`: `Token`, `Location` (offset is 0-based; line and column
  are 1-based) and `UnmatchedText`.
- `scanner/logger.py`: logs to the `"lectes.scanner"` logger. Importing lectes
  adds a single `NullHandler` on `"lectes"`. `debug=True` writes only that
  scanner's events to stderr, and adds no handlers.
- `cli.py` and `__main__.py`: the `lectes GRAMMAR [INPUT]` command, built on
  argparse. Exit codes are 0 for success, 1 for unmatched text, and 2 for a
  usage, grammar or I/O error. It's exposed via `[project.scripts]`.

The grammar format is one `NAME  regex` rule per line, with `#` comments. It's
shared with lectes-web, which lives in `../lectes-web`.

## Rules

- **No runtime dependencies.** Use the stdlib only, the CLI included. Adding a
  runtime dependency needs explicit approval. Dev-only tools go in the `dev`
  dependency group.
- **Python 3.13+** (`requires-python = ">=3.13"`). Modern syntax is fine.
- **The public API is stable.** It covers:
  - everything exported from `src/lectes/__init__.py`;
  - `Configuration.from_text`'s errors and warnings;
  - the CLI's arguments, output formats and exit codes.

  lectes-web pins lectes and depends on all of this. Point out any breaking
  change and get agreement before making it. Record it under
  `### Breaking changes` in the CHANGELOG.
- New public names go in `src/lectes/__init__.py` (as `from .x import Y as Y`),
  with an identity check in `tests/unit/test_package.py` or the module's own
  tests.

## Workflow

- **Test first, always.** For every behaviour change or bug fix:
  1. Write the tests.
  2. Run them and watch them fail.
  3. Implement until they pass.

  Tests and implementation go in the same commit.
- **Tests** use `unittest` with `unittest-extensions`. A test class defines
  `subject(...)`, test methods are decorated with `@args(...)`, and they call
  `self.result()`, `self.assertResult(...)` or
  `self.assertResultRaises(...)`. Shared setup and assert helpers go on a base
  `TestCase`. Tests mirror the package under `src/lectes/tests/unit/`. CLI tests
  call `main([...])` with stdin, stdout and stderr patched.
- **Git:**
  - Always work on a branch, never directly on `main`.
  - Make small atomic commits, each one passing the checks.
  - Write commit subjects in the present tense, third person, e.g. "Adds …",
    "Fixes …", "Documents …", "Bumps version to X.Y.Z". Add a body explaining
    *why* when it isn't obvious.
  - Don't merge into `main`, push, tag, publish or deploy docs unless asked.
    When asked to merge, use `git merge --no-ff <branch>` (message:
    `Merge branch '<branch>'`).
- **Docs go with every user-facing change, on the same branch:**
  - Update the relevant `docs/*.md` page and, if needed, `README.md`.
  - Add a bullet under `## X.Y.Z - Unreleased` in `CHANGELOG.md`, in the
    `Breaking changes` / `Added` / `Changed` / `Fixed` sections.
  - New pages go in the `mkdocs.yml` nav. API pages are `::: module` stubs
    rendered by mkdocstrings.
- **Code style:**
  - Formatting is ruff's.
  - Type hints everywhere. Prefix private helpers with `_`.
  - Public docstrings explain the behaviour, with `## Example` blocks and
    `Raises:` / `Warns:` sections, because mkdocstrings renders them.
  - Error messages are lowercase and show user values with `repr`.
- `PLAN.md` and `.python-version` are the user's untracked files. Don't commit
  them.

## Release (only when asked)

1. On the branch:
   - Set `version` in `pyproject.toml`.
   - Run `uv lock`.
   - Change `## X.Y.Z - Unreleased` to today's date.
   - Commit as "Bumps version to X.Y.Z".
2. Merge into `main` with `--no-ff`, run `make test`, then
   `git push origin main`.
3. Run `git tag X.Y.Z` (no `v` prefix), then `git push origin X.Y.Z`.
4. Run `make clean build`. Check that `dist/` holds only
   X.Y.Z, and that the wheel has what you expect (e.g.
   `unzip -l dist/*.whl`).
5. Run `make publish`. `UV_PUBLISH_TOKEN` comes from `.envrc` (via direnv, and
   git-ignored). Never print it.
6. Run `make deploy-documentation`. GitHub Pages takes a few minutes to
   rebuild. Check progress with `gh api repos/Maxcode123/lectes/pages/builds/latest`.
7. Verify with `uvx --refresh --from lectes==X.Y.Z lectes --version`, and check
   the changed docs pages on the live site.

Pitfalls:

- Never build unreleased code into `dist/` under an already-released version
  number. To try a local build, use `uv build -o <scratch dir>` or
  `uvx --from . lectes`.
- Plain `uvx lectes` runs the latest version on PyPI, not this checkout.
