from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics

from .layout import avery_template, label_positions, validate_template_spec


def _format_address(row: dict) -> list[str]:
    first = " ".join(x for x in [row.get("title", ""), row.get("name", ""), row.get("surname", "")] if x).strip()
    title_line = (row.get("title_line_1", "") or "").strip()
    ordered = [title_line, first, row.get("address", ""), row.get("country", "")]
    return [line for line in ordered if line]


def _resolve_template(template_spec_or_code):
    if isinstance(template_spec_or_code, dict):
        return validate_template_spec(template_spec_or_code)
    return avery_template(template_spec_or_code)


def render_labels_pdf(addresses, template_spec_or_code, output_path, top_margin_mm=0, right_margin_mm=0, bottom_margin_mm=0, left_margin_mm=0, sender_address="", font_family="Helvetica"):

    tpl = _resolve_template(template_spec_or_code)
    per_page = int(tpl["rows"]) * int(tpl["cols"])

    c = canvas.Canvas(output_path, pagesize=A4)
    boxes = label_positions(tpl, top_margin_mm, right_margin_mm, bottom_margin_mm, left_margin_mm)

    for idx, row in enumerate(addresses):
        if idx > 0 and idx % per_page == 0:
            c.showPage()

        x, y_top, w, h = boxes[idx % per_page]
        y = A4[1] - y_top - h

        # Sender block (small + highlighted)
        sender_lines = [ln.strip() for ln in (sender_address or "").splitlines() if ln.strip()]
        if sender_lines:
            sender_text = c.beginText(x + 6, y + h - 10)
            sender_text.setFont(font_family, 6.8)
            sender_text.setLeading(7.5)
            sender_first = sender_lines[0]
            sender_text.textLine(sender_first)
            if len(sender_lines) > 1:
                sender_text.textLine(sender_lines[1])
            c.drawText(sender_text)
            # underline first sender line
            underline_y = y + h - 12
            c.setLineWidth(0.6)
            text_w = pdfmetrics.stringWidth(sender_first, font_family, 6.8)
            end_x = min(x + 6 + text_w, x + w - 6)
            c.line(x + 6, underline_y, end_x, underline_y)
            start_y = y + h - 26
        else:
            start_y = y + h - 14

        lines = _format_address(row)
        text = c.beginText(x + 6, start_y)
        text.setFont(font_family, 10)
        text.setLeading(12)
        for line in lines:
            text.textLine(line)
        c.drawText(text)

    c.save()
