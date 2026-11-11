# lintdiff

Show only changed lint rules between two lint reports.

## About

`lintdiff` compares two lint reports and reports only the rules that changed between
them. It is designed to sit in front of `ruff`, `eslint`, or similar tools that emit
machine-readable lint results. Instead of re-reading every warning on every run,
you can diff against a saved baseline and focus on regressions and new issues.

The tool accepts the JSON output formats used by `ruff check --output-format json`
and many other linters, because those formats share a common `path` / `line` /
`code` / `message` shape.

## Features

- Added / removed / unchanged classification per rule.
- Plain-text and Markdown output.
- Filter to `added` or `removed` only.
- Zero runtime dependencies beyond the Python standard library.
- Works with `ruff` JSON output out of the box.

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
# Generate a baseline once.
ruff check . --output-format json > baseline.json

# After code changes, generate a fresh report and diff.
ruff check . --output-format json > current.json
lintdiff baseline.json current.json
```

```text
+ F401 src/app.py:12: `os` imported but unused
- E501 src/app.py:99: line too long (105 > 100 characters)
```

```bash
# Markdown output.
lintdiff --format markdown baseline.json current.json

# Only added rules.
lintdiff --only added baseline.json current.json

# Only removed rules.
lintdiff --only removed baseline.json current.json
```

## stdin / piping

You can also pipe reports into `lintdiff` by naming one side `-`:

```bash
ruff check . --output-format json | lintdiff - current.json
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Reports compared successfully |
| 1    | Invalid input path or malformed report |

## Project structure

```
LICENSE
README.md
lintdiff.py
pyproject.toml
tests/
└── test_lintdiff.py
```

## Tags / keywords

lint diff cli ruff static-analysis git changed-rules regression
