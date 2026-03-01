from dataclasses import dataclass
from datetime import datetime
import base64
import io
import os

from flask import Flask, Response, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from .csv_parser import parse_addresses
from .i18n import normalize_lang, t, tf
from .layout import list_avery_templates
from .pdf_render import render_labels_pdf

SAMPLE_CSV = """title_line_1,title,name,surname,address,country
INVITATION,Dr,Jane,Doe,1 Main St,NL
,Mr,John,Smith,2 River Rd,FR
"""

ALLOWED_CSV_MIME_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
}


@dataclass
class ParsedForm:
    addresses: list
    csv_text: str
    template_spec: dict | str
    template_name: str
    top: float
    right: float
    bottom: float
    left: float
    sender_address: str
    font_family: str


def _lang_from_request(req) -> str:
    return normalize_lang(req.values.get("lang") or req.args.get("lang"))


def _decode_csv_bytes(raw: bytes) -> str:
    if raw.startswith(b"%PDF"):
        raise ValueError("Please upload a CSV file (.csv), not a PDF")
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            if "\x00" in text:
                raise ValueError("Invalid CSV content")
            return text
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode CSV file. Please save it as UTF-8.")


def _parse_custom_template(req) -> dict:
    return {
        "rows": int(req.form.get("custom_rows", "0") or 0),
        "cols": int(req.form.get("custom_cols", "0") or 0),
        "label_width_mm": float(req.form.get("custom_label_width_mm", "0") or 0),
        "label_height_mm": float(req.form.get("custom_label_height_mm", "0") or 0),
        "pitch_x_mm": float(req.form.get("custom_pitch_x_mm", "0") or 0),
        "pitch_y_mm": float(req.form.get("custom_pitch_y_mm", "0") or 0),
        "origin_x_mm": float(req.form.get("custom_origin_x_mm", "0") or 0),
        "origin_y_mm": float(req.form.get("custom_origin_y_mm", "0") or 0),
    }


def _parse_template(req) -> tuple[dict | str, str]:
    template = req.form.get("template", "L7160")
    return (_parse_custom_template(req), "CUSTOM") if template == "CUSTOM" else (template, template)


def _extract_csv_text(req) -> str:
    uploaded = req.files.get("csv_file")
    if not uploaded or not uploaded.filename:
        return req.form.get("csv_text", "")

    filename = (uploaded.filename or "").lower()
    if not filename.endswith(".csv"):
        raise ValueError("Please upload a CSV file (.csv)")
    if uploaded.mimetype and uploaded.mimetype not in ALLOWED_CSV_MIME_TYPES:
        raise ValueError("Unsupported file type. Please upload a CSV file")

    raw = uploaded.read()
    if not raw:
        raise ValueError("CSV file is empty")
    return _decode_csv_bytes(raw)


def _parse_float(req, key: str, default: float = 0.0) -> float:
    return float(req.form.get(key, default) or default)


def _extract_form(req) -> ParsedForm:
    csv_text = _extract_csv_text(req)
    template_spec, template_name = _parse_template(req)
    return ParsedForm(
        addresses=parse_addresses(csv_text),
        csv_text=csv_text,
        template_spec=template_spec,
        template_name=template_name,
        top=_parse_float(req, "top_margin"),
        right=_parse_float(req, "right_margin"),
        bottom=_parse_float(req, "bottom_margin"),
        left=_parse_float(req, "left_margin"),
        sender_address=(req.form.get("sender_address", "") or "").strip(),
        font_family=(req.form.get("font_family", "Helvetica") or "Helvetica").strip(),
    )


def _make_pdf_buffer(form: ParsedForm) -> io.BytesIO:
    pdf_buffer = io.BytesIO()
    render_labels_pdf(
        form.addresses,
        form.template_spec,
        pdf_buffer,
        form.top,
        form.right,
        form.bottom,
        form.left,
        sender_address=form.sender_address,
        font_family=form.font_family,
    )
    return pdf_buffer


def _render_index(lang: str, ga_measurement_id: str, error: str | None = None, status: int = 200):
    return (
        render_template(
            "index.html",
            templates=list_avery_templates(),
            error=error,
            lang=lang,
            tr=lambda k: t(lang, k),
            ga_measurement_id=ga_measurement_id,
        ),
        status,
    )


def _set_security_headers(resp):
    csp = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; "
        "connect-src 'self' https://www.google-analytics.com; frame-src 'self' data:; "
        "object-src 'self' data:; base-uri 'self'; frame-ancestors 'self'"
    )
    resp.headers.setdefault("Content-Security-Policy", csp)
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return resp


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_BYTES", "1048576"))
    ga_measurement_id = os.getenv("GA_MEASUREMENT_ID", "").strip()

    @app.after_request
    def set_security_headers(resp):
        return _set_security_headers(resp)

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(_e):
        lang = _lang_from_request(request)
        return _render_index(lang, ga_measurement_id, "Uploaded file is too large. Please keep CSV files under 1MB.", 413)

    @app.get("/")
    def index():
        lang = _lang_from_request(request)
        return _render_index(lang, ga_measurement_id)[0]

    @app.get("/sample.csv")
    def sample_csv():
        return Response(SAMPLE_CSV, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=sample_addresses.csv"})

    @app.post("/preview")
    def preview():
        lang = _lang_from_request(request)
        try:
            form = _extract_form(request)
        except ValueError as e:
            return _render_index(lang, ga_measurement_id, str(e), 400)

        pdf_data_uri = "data:application/pdf;base64," + base64.b64encode(_make_pdf_buffer(form).getvalue()).decode("ascii")
        return render_template(
            "preview.html",
            preview_rows=form.addresses[:12],
            csv_text=form.csv_text,
            template=form.template_name,
            top_margin=form.top,
            right_margin=form.right,
            bottom_margin=form.bottom,
            left_margin=form.left,
            template_spec=form.template_spec if isinstance(form.template_spec, dict) else None,
            templates=list_avery_templates(),
            lang=lang,
            tr=lambda k: t(lang, k),
            tf=lambda k, **kw: tf(lang, k, **kw),
            sender_address=form.sender_address,
            font_family=form.font_family,
            pdf_data_uri=pdf_data_uri,
        )

    @app.post("/generate")
    def generate():
        lang = _lang_from_request(request)
        try:
            form = _extract_form(request)
        except ValueError as e:
            return _render_index(lang, ga_measurement_id, str(e), 400)

        pdf_buffer = _make_pdf_buffer(form)
        pdf_buffer.seek(0)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"labels_{form.template_name}_{ts}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
