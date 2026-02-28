from flask import Flask, render_template, request, send_file, Response
import tempfile

from .csv_parser import parse_addresses
from .layout import list_avery_templates
from .pdf_render import render_labels_pdf


SAMPLE_CSV = """title,name,surname,address,country
Dr,Jane,Doe,1 Main St,NL
Mr,John,Smith,2 River Rd,FR
"""


def _extract_form_and_addresses(req):
    csv_text = ""
    if "csv_file" in req.files and req.files["csv_file"].filename:
        csv_text = req.files["csv_file"].read().decode("utf-8")
    else:
        csv_text = req.form.get("csv_text", "")

    addresses = parse_addresses(csv_text)
    template = req.form.get("template", "L7160")
    top = float(req.form.get("top_margin", 0) or 0)
    right = float(req.form.get("right_margin", 0) or 0)
    bottom = float(req.form.get("bottom_margin", 0) or 0)
    left = float(req.form.get("left_margin", 0) or 0)
    return addresses, csv_text, template, top, right, bottom, left


def create_app():
    app = Flask(__name__, template_folder="../templates")

    @app.get("/")
    def index():
        return render_template("index.html", templates=list_avery_templates())

    @app.get("/sample.csv")
    def sample_csv():
        return Response(
            SAMPLE_CSV,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=sample_addresses.csv"},
        )

    @app.post("/preview")
    def preview():
        addresses, csv_text, template, top, right, bottom, left = _extract_form_and_addresses(request)
        preview_rows = addresses[:12]
        return render_template(
            "preview.html",
            preview_rows=preview_rows,
            csv_text=csv_text,
            template=template,
            top_margin=top,
            right_margin=right,
            bottom_margin=bottom,
            left_margin=left,
            templates=list_avery_templates(),
        )

    @app.post("/generate")
    def generate():
        addresses, _csv_text, template, top, right, bottom, left = _extract_form_and_addresses(request)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            out = tmp.name

        render_labels_pdf(addresses, template, out, top, right, bottom, left)
        return send_file(out, as_attachment=True, download_name="labels.pdf", mimetype="application/pdf")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
