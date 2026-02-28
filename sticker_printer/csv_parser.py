import csv
from io import StringIO

REQUIRED_FIELDS = {"name", "surname", "address", "country"}


def parse_addresses(csv_text: str):
    reader = csv.DictReader(StringIO(csv_text.strip()))
    if not reader.fieldnames:
        raise ValueError("CSV must have headers")

    missing = REQUIRED_FIELDS - set(h.strip() for h in reader.fieldnames)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

    rows = []
    for idx, row in enumerate(reader, start=2):
        clean = {k.strip(): (v or "").strip() for k, v in row.items()}
        clean.setdefault("title", "")

        for field in sorted(REQUIRED_FIELDS):
            if not clean.get(field):
                raise ValueError(f"Missing value for '{field}' at row {idx}")

        rows.append(clean)

    if not rows:
        raise ValueError("CSV must contain at least one row")

    return rows
