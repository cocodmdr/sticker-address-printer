from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .layout import avery_template, label_positions, validate_template_spec


def _format_address(row: dict) -> list[str]:
    first = " ".join(x for x in [row.get("title", ""), row.get("name", ""), row.get("surname", "")] if x).strip()
    return [line for line in [first, row.get("address", ""), row.get("country", "")] if line]


def _resolve_template(template_spec_or_code):
    if isinstance(template_spec_or_code, dict):
        return validate_template_spec(template_spec_or_code)
    return avery_template(template_spec_or_code)


def render_labels_pdf(addresses, template_spec_or_code, output_path, top_margin_mm=0, right_margin_mm=0, bottom_margin_mm=0, left_margin_mm=0):
    tpl = _resolve_template(template_spec_or_code)
    per_page = int(tpl["rows"]) * int(tpl["cols"])

    c = canvas.Canvas(output_path, pagesize=A4)
    boxes = label_positions(tpl, top_margin_mm, right_margin_mm, bottom_margin_mm, left_margin_mm)

    for idx, row in enumerate(addresses):
        if idx > 0 and idx % per_page == 0:
            c.showPage()

        x, y_top, w, h = boxes[idx % per_page]
        y = A4[1] - y_top - h

        lines = _format_address(row)
        text = c.beginText(x + 6, y + h - 14)
        text.setFont("Helvetica", 10)
        text.setLeading(12)
        for line in lines:
            text.textLine(line)
        c.drawText(text)

    c.save()
