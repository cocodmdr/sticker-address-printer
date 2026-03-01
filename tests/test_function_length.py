import ast
from pathlib import Path

MAX_LINES = 10
ALLOWED_LONG = {"create_app"}


def _function_length(node: ast.FunctionDef) -> int:
    end = getattr(node, "end_lineno", node.lineno)
    return end - node.lineno + 1


def test_function_length_budget():
    src = Path("sticker_printer/web.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name not in ALLOWED_LONG:
            ln = _function_length(n)
            if ln > MAX_LINES:
                offenders.append((n.name, ln))
    assert not offenders, f"Functions too long: {offenders}"
