import csv
from io import StringIO

REQUIRED_FIELDS = {"name", "surname", "address", "country"}


def _csv_reader(csv_text: str):
    return csv.DictReader(StringIO(csv_text.strip()))


def _missing_headers(fieldnames) -> set[str]:
    return REQUIRED_FIELDS - set(h.strip() for h in (fieldnames or []))


def _clean_row(row: dict) -> dict:
    clean = {k.strip(): (v or "").strip() for k, v in row.items()}
    clean.setdefault("title", "")
    return clean


def _missing_required_value(clean: dict) -> str | None:
    return next((f for f in sorted(REQUIRED_FIELDS) if not clean.get(f)), None)


def _validate_headers(reader):
    if not reader.fieldnames:
        raise ValueError("CSV must have headers")
    missing = _missing_headers(reader.fieldnames)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")


def _parse_rows(reader) -> list[dict]:
    rows = []
    for idx, row in enumerate(reader, start=2):
        clean = _clean_row(row)
        missing = _missing_required_value(clean)
        if missing:
            raise ValueError(f"Missing value for '{missing}' at row {idx}")
        rows.append(clean)
    return rows


def _ensure_non_empty(rows: list[dict]):
    if not rows:
        raise ValueError("CSV must contain at least one row")


def parse_addresses(csv_text: str):
    reader = _csv_reader(csv_text)
    _validate_headers(reader)
    rows = _parse_rows(reader)
    _ensure_non_empty(rows)
    return rows
