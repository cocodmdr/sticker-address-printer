from datetime import datetime
from flask import Flask, render_template, request, send_file, Response
import tempfile


def _decode_csv_bytes(raw: bytes) -> str:
    """Decode uploaded CSV with common encodings from spreadsheet exports."""
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode CSV file. Please save it as UTF-8.")


from .csv_parser import parse_addresses
from .layout import list_avery_templates
from .pdf_render import render_labels_pdf
from .i18n import normalize_lang, t


SAMPLE_CSV = """title,name,surname,address,country
Dr,Jane,Doe,1 Main St,NL
Mr,John,Smith,2 River Rd,FR
"""


def _parse_template(req):
    template = req.form.get("template", "L7160")
    if template != "CUSTOM":
        return template, template

    spec = {
        "rows": int(req.form.get("custom_rows", "0") or 0),
        "cols": int(req.form.get("custom_cols", "0") or 0),
        "label_width_mm": float(req.form.get("custom_label_width_mm", "0") or 0),
        "label_height_mm": float(req.form.get("custom_label_height_mm", "0") or 0),
        "pitch_x_mm": float(req.form.get("custom_pitch_x_mm", "0") or 0),
        "pitch_y_mm": float(req.form.get("custom_pitch_y_mm", "0") or 0),
        "origin_x_mm": float(req.form.get("custom_origin_x_mm", "0") or 0),
        "origin_y_mm": float(req.form.get("custom_origin_y_mm", "0") or 0),
    }
    return spec, "CUSTOM"


def _extract_form_and_addresses(req):
    csv_text = ""
    if "csv_file" in req.files and req.files["csv_file"].filename:
        filename = req.files["csv_file"].filename.lower()
        if not filename.endswith(".csv"):
            raise ValueError("Please upload a CSV file (.csv)")
        raw = req.files["csv_file"].read()
        csv_text = _decode_csv_bytes(raw)
    else:
        csv_text = req.form.get("csv_text", "")

    addresses = parse_addresses(csv_text)
    template_spec, template_name = _parse_template(req)
    top = float(req.form.get("top_margin", 0) or 0)
    right = float(req.form.get("right_margin", 0) or 0)
    bottom = float(req.form.get("bottom_margin", 0) or 0)
    left = float(req.form.get("left_margin", 0) or 0)
    return addresses, csv_text, template_spec, template_name, top, right, bottom, left


def _lang_from_request(req):
    return normalize_lang(req.values.get("lang") or req.args.get("lang"))


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="/static")

    @app.get("/")
    def index():
        lang = _lang_from_request(request)
        return render_template("index.html", templates=list_avery_templates(), error=None, lang=lang, tr=lambda k: t(lang, k))

    @app.get("/sample.csv")
    def sample_csv():
        return Response(
            SAMPLE_CSV,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=sample_addresses.csv"},
        )

    @app.post("/preview")
    def preview():
        try:
            addresses, csv_text, template_spec, template_name, top, right, bottom, left = _extract_form_and_addresses(request)
        except ValueError as e:
            lang = _lang_from_request(request)
            return (
                render_template("index.html", templates=list_avery_templates(), error=str(e), lang=lang, tr=lambda k: t(lang, k)),
                400,
            )

        preview_rows = addresses[:12]
        lang = _lang_from_request(request)
        return render_template(
            "preview.html",
            preview_rows=preview_rows,
            csv_text=csv_text,
            template=template_name,
            top_margin=top,
            right_margin=right,
            bottom_margin=bottom,
            left_margin=left,
            template_spec=template_spec if isinstance(template_spec, dict) else None,
            templates=list_avery_templates(),
            lang=lang,
            tr=lambda k: t(lang, k),
        )

    @app.post("/generate")
    def generate():
        try:
            addresses, _csv_text, template_spec, template_name, top, right, bottom, left = _extract_form_and_addresses(request)
        except ValueError as e:
            lang = _lang_from_request(request)
            return (
                render_template("index.html", templates=list_avery_templates(), error=str(e), lang=lang, tr=lambda k: t(lang, k)),
                400,
            )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            out = tmp.name

        render_labels_pdf(addresses, template_spec, out, top, right, bottom, left)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"labels_{template_name}_{ts}.pdf"
        return send_file(out, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
