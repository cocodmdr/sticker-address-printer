import ast
from pathlib import Path

MAX_LINES = 10
ALLOWED_LONG = {"create_app"}


def _function_length(node: ast.FunctionDef) -> int:
    end = getattr(node, "end_lineno", node.lineno)
    return end - node.lineno + 1


def _module_offenders(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name not in ALLOWED_LONG:
            ln = _function_length(n)
            if ln > MAX_LINES:
                offenders.append((n.name, ln))
    return offenders


def test_function_length_budget():
    offenders = {}
    for path in Path("sticker_printer").glob("*.py"):
        if path.name == "__init__.py":
            continue
        module_off = _module_offenders(path)
        if module_off:
            offenders[path.name] = module_off
    assert not offenders, f"Functions too long: {offenders}"
