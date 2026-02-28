from flask import Flask, render_template, request, send_file
import tempfile

from .csv_parser import parse_addresses
from .pdf_render import render_labels_pdf


def create_app():
    app = Flask(__name__, template_folder="../templates")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/generate")
    def generate():
        csv_file = request.files["csv_file"]
        csv_text = csv_file.read().decode("utf-8")
        addresses = parse_addresses(csv_text)

        template = request.form.get("template", "L7160")
        top = float(request.form.get("top_margin", 0) or 0)
        right = float(request.form.get("right_margin", 0) or 0)
        bottom = float(request.form.get("bottom_margin", 0) or 0)
        left = float(request.form.get("left_margin", 0) or 0)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            out = tmp.name

        render_labels_pdf(addresses, template, out, top, right, bottom, left)
        return send_file(out, as_attachment=True, download_name="labels.pdf", mimetype="application/pdf")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
