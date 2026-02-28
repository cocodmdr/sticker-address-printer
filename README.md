# Sticker Address Printer

A small web app to print address labels on Avery sticker sheets.

## Features
- Upload CSV with columns: `title,name,surname,address,country`
- Select Avery template (currently `L7160`)
- Tune top/right/bottom/left margins (mm)
- Generate printable PDF labels

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m sticker_printer.web
```
Then open http://127.0.0.1:5000

## Tests (TDD)
```bash
source .venv/bin/activate
pytest -q
```

## Design notes
- `csv_parser.py`: input parsing/validation
- `layout.py`: Avery geometry and coordinate calculation
- `pdf_render.py`: PDF rendering service
- `web.py`: Flask delivery layer

This keeps responsibilities separated (SOLID/SRP) and makes units testable.
