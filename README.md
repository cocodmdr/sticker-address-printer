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


## Free hosting (Render)
This project includes `render.yaml` and `Procfile`.

1. Push to GitHub
2. Go to Render and create a **Web Service** from the repo
3. Use free plan
4. Deploy

## Quick local test
```bash
source .venv/bin/activate
pytest -q
python -m sticker_printer.web
```
Open http://127.0.0.1:5000


## Traffic analytics (Google Analytics)
Set environment variable `GA_MEASUREMENT_ID` (example: `G-XXXXXXXXXX`).
When set, the homepage injects gtag.js.

On Render: Service -> Environment -> add `GA_MEASUREMENT_ID` and redeploy.


### GDPR-friendly analytics consent
When `GA_MEASUREMENT_ID` is set, a cookie-consent banner is shown.
- **Accept**: loads Google Analytics (gtag)
- **Reject**: GA is not loaded
Consent choice is stored in `localStorage` key `cookie_consent_v1`.
