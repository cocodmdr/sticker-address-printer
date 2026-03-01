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


def _raise_if_pdf(raw: bytes):
    if raw.startswith(b"%PDF"):
        raise ValueError("Please upload a CSV file (.csv), not a PDF")


def _raise_if_invalid_text(text: str):
    if "\x00" in text:
        raise ValueError("Invalid CSV content")


def _decode_with_encoding(raw: bytes, enc: str) -> str | None:
    try:
        return raw.decode(enc)
    except UnicodeDecodeError:
        return None


def _decode_csv_bytes(raw: bytes) -> str:
    _raise_if_pdf(raw)
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        text = _decode_with_encoding(raw, enc)
        if text is not None:
            _raise_if_invalid_text(text)
            return text
    raise ValueError("Unable to decode CSV file. Please save it as UTF-8.")


def _as_int(req, key: str) -> int:
    return int(req.form.get(key, "0") or 0)


def _as_float(req, key: str, default: float = 0.0) -> float:
    return float(req.form.get(key, default) or default)


def _parse_custom_template(req) -> dict:
    return {"rows": _as_int(req, "custom_rows"), "cols": _as_int(req, "custom_cols"), "label_width_mm": _as_float(req, "custom_label_width_mm"), "label_height_mm": _as_float(req, "custom_label_height_mm"), "pitch_x_mm": _as_float(req, "custom_pitch_x_mm"), "pitch_y_mm": _as_float(req, "custom_pitch_y_mm"), "origin_x_mm": _as_float(req, "custom_origin_x_mm"), "origin_y_mm": _as_float(req, "custom_origin_y_mm")}


def _parse_template(req) -> tuple[dict | str, str]:
    template = req.form.get("template", "L7160")
    return (_parse_custom_template(req), "CUSTOM") if template == "CUSTOM" else (template, template)


def _is_valid_csv_upload(uploaded) -> bool:
    return bool(uploaded and uploaded.filename)


def _validate_csv_name(uploaded):
    if not (uploaded.filename or "").lower().endswith(".csv"):
        raise ValueError("Please upload a CSV file (.csv)")


def _validate_csv_mime(uploaded):
    if uploaded.mimetype and uploaded.mimetype not in ALLOWED_CSV_MIME_TYPES:
        raise ValueError("Unsupported file type. Please upload a CSV file")


def _read_non_empty(uploaded) -> bytes:
    raw = uploaded.read()
    if not raw:
        raise ValueError("CSV file is empty")
    return raw


def _extract_csv_text(req) -> str:
    uploaded = req.files.get("csv_file")
    if not _is_valid_csv_upload(uploaded):
        return req.form.get("csv_text", "")
    _validate_csv_name(uploaded)
    _validate_csv_mime(uploaded)
    return _decode_csv_bytes(_read_non_empty(uploaded))


def _sender_address(req) -> str:
    return (req.form.get("sender_address", "") or "").strip()


def _font_family(req) -> str:
    return (req.form.get("font_family", "Helvetica") or "Helvetica").strip()


def _extract_form(req) -> ParsedForm:
    csv_text = _extract_csv_text(req)
    template_spec, template_name = _parse_template(req)
    return ParsedForm(parse_addresses(csv_text), csv_text, template_spec, template_name, _as_float(req, "top_margin"), _as_float(req, "right_margin"), _as_float(req, "bottom_margin"), _as_float(req, "left_margin"), _sender_address(req), _font_family(req))


def _make_pdf_buffer(form: ParsedForm) -> io.BytesIO:
    pdf_buffer = io.BytesIO()
    render_labels_pdf(form.addresses, form.template_spec, pdf_buffer, form.top, form.right, form.bottom, form.left, sender_address=form.sender_address, font_family=form.font_family)
    return pdf_buffer


def _pdf_data_uri(form: ParsedForm) -> str:
    return "data:application/pdf;base64," + base64.b64encode(_make_pdf_buffer(form).getvalue()).decode("ascii")


def _template_ctx(lang: str, ga_measurement_id: str) -> dict:
    return {"templates": list_avery_templates(), "lang": lang, "tr": lambda k: t(lang, k), "ga_measurement_id": ga_measurement_id}


def _render_index(lang: str, ga_measurement_id: str, error: str | None = None, status: int = 200):
    ctx = _template_ctx(lang, ga_measurement_id)
    return render_template("index.html", error=error, **ctx), status


def _security_csp() -> str:
    return (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; "
        "connect-src 'self' https://www.google-analytics.com; frame-src 'self' data:; "
        "object-src 'self' data:; base-uri 'self'; frame-ancestors 'self'"
    )


def _set_security_headers(resp):
    resp.headers.setdefault("Content-Security-Policy", _security_csp())
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return resp


def _preview_context(form: ParsedForm, lang: str, ga_measurement_id: str) -> dict:
    base = _template_ctx(lang, ga_measurement_id)
    base.update({"preview_rows": form.addresses[:12], "csv_text": form.csv_text, "template": form.template_name, "top_margin": form.top, "right_margin": form.right, "bottom_margin": form.bottom, "left_margin": form.left, "template_spec": form.template_spec if isinstance(form.template_spec, dict) else None, "tf": lambda k, **kw: tf(lang, k, **kw), "sender_address": form.sender_address, "font_family": form.font_family, "pdf_data_uri": _pdf_data_uri(form)})
    return base


def _pdf_download_name(template_name: str) -> str:
    return f"labels_{template_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_BYTES", "1048576"))
    ga_measurement_id = os.getenv("GA_MEASUREMENT_ID", "").strip()

    @app.after_request
    def set_security_headers(resp):
        return _set_security_headers(resp)

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(_e):
        return _render_index(_lang_from_request(request), ga_measurement_id, "Uploaded file is too large. Please keep CSV files under 1MB.", 413)

    @app.get("/")
    def index():
        return _render_index(_lang_from_request(request), ga_measurement_id)[0]

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
        return render_template("preview.html", **_preview_context(form, lang, ga_measurement_id))

    @app.post("/generate")
    def generate():
        lang = _lang_from_request(request)
        try:
            form = _extract_form(request)
        except ValueError as e:
            return _render_index(lang, ga_measurement_id, str(e), 400)
        pdf_buffer = _make_pdf_buffer(form)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name=_pdf_download_name(form.template_name), mimetype="application/pdf")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
