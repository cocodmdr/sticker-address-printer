# Contributing

Thanks for contributing.

## Development workflow (TDD)
1. Write a failing test first.
2. Implement the smallest change to pass tests.
3. Refactor while keeping tests green.
4. Make atomic commits.

## Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python -m sticker_printer.web
```

## Commit style
- `test:` tests only
- `feat:` behavior change
- `refactor:` internal cleanup
- `docs:` documentation
