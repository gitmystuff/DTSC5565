# Where and How to Run pytest

## Where

From your **project root** — the same folder that has `router.py`,
`agent.py`, and `pyproject.toml` — not from inside the `tests/` folder
itself.

Your folder should look like this:

```
your-agent-project/
├── router.py
├── agent.py
├── conftest.py      ← empty, see note below
└── tests/
    └── test_tools.py
```

## How

1. Make sure pytest is actually installed in the project (if you haven't
   yet):

```bash
uv add --dev pytest
```

2. From the project root, run:

```bash
uv run pytest
```

or, more verbose (shows each test name and pass/fail):

```bash
uv run pytest -v
```

`uv run pytest` will automatically discover `tests/test_tools.py`
because it matches the `test_*.py` naming convention — no need to point
it at the file directly.

## If you hit an import error

If you get `ModuleNotFoundError: No module named 'router'`, add an empty
`conftest.py` file at the project root — the same trick from the pytest
lecture a few weeks back. Its *presence*, not its content, is what tells
pytest "this is the project root" and adds it to Python's import path,
which is what lets `test_tools.py` do
`from router import calculate_average, check_password_strength` without
any manual path setup.

```bash
touch conftest.py
```

### A docstring for conftest.py

Same pattern as the `basic-pytest-example` repo from a few weeks back —
the file's job is just to exist in the right place, so the docstring
should say that plainly. This is the whole file — just the docstring,
nothing else:

```python
"""
conftest.py

This file is intentionally empty of real logic.

Its presence tells pytest "this is the project root" and causes pytest to
add this directory to sys.path automatically. That's what lets
tests/test_tools.py do `from router import calculate_average,
check_password_strength` without any extra configuration.
"""
```

Not every file's value is in what it contains.
