from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from .layout import avery_template, label_positions, validate_template_spec


def _name_line(row: dict) -> str:
    parts = [row.get("title", ""), row.get("name", ""), row.get("surname", "")]
    return " ".join(x for x in parts if x).strip()


def _format_address(row: dict) -> list[str]:
    lines = [(row.get("title_line_1", "") or "").strip(), _name_line(row), row.get("address", ""), row.get("country", "")]
    return [line for line in lines if line]


def _resolve_template(template_spec_or_code):
    return validate_template_spec(template_spec_or_code) if isinstance(template_spec_or_code, dict) else avery_template(template_spec_or_code)


def _new_canvas(output_path):
    return canvas.Canvas(output_path, pagesize=A4)


def _page_slot(idx: int, per_page: int) -> int:
    return idx % per_page


def _start_new_page_if_needed(c, idx: int, per_page: int):
    if idx > 0 and idx % per_page == 0:
        c.showPage()


def _label_frame(box):
    x, y_top, w, h = box
    return x, A4[1] - y_top - h, w, h


def _sender_lines(sender_address: str) -> list[str]:
    return [ln.strip() for ln in (sender_address or "").splitlines() if ln.strip()]


def _underline_sender(c, text: str, x: float, y: float, h: float, w: float, font_family: str):
    y_line = y + h - 12
    width = pdfmetrics.stringWidth(text, font_family, 6.8)
    c.setLineWidth(0.6)
    c.line(x + 6, y_line, min(x + 6 + width, x + w - 6), y_line)


def _draw_sender(c, lines: list[str], x: float, y: float, w: float, h: float, font_family: str) -> float:
    t = c.beginText(x + 6, y + h - 10)
    t.setFont(font_family, 6.8)
    t.setLeading(7.5)
    t.textLine(lines[0])
    if len(lines) > 1:
        t.textLine(lines[1])
    c.drawText(t)
    _underline_sender(c, lines[0], x, y, h, w, font_family)
    return y + h - 26


def _content_start_y(c, sender_address: str, x: float, y: float, w: float, h: float, font_family: str) -> float:
    lines = _sender_lines(sender_address)
    return _draw_sender(c, lines, x, y, w, h, font_family) if lines else (y + h - 14)


def _draw_address_lines(c, lines: list[str], x: float, start_y: float, font_family: str):
    t = c.beginText(x + 6, start_y)
    t.setFont(font_family, 10)
    t.setLeading(12)
    for line in lines:
        t.textLine(line)
    c.drawText(t)


def _draw_label(c, row: dict, box, sender_address: str, font_family: str):
    x, y, w, h = _label_frame(box)
    start_y = _content_start_y(c, sender_address, x, y, w, h, font_family)
    _draw_address_lines(c, _format_address(row), x, start_y, font_family)


def render_labels_pdf(addresses, template_spec_or_code, output_path, top_margin_mm=0, right_margin_mm=0, bottom_margin_mm=0, left_margin_mm=0, sender_address="", font_family="Helvetica"):
    tpl = _resolve_template(template_spec_or_code)
    per_page = int(tpl["rows"]) * int(tpl["cols"])
    c = _new_canvas(output_path)
    boxes = label_positions(tpl, top_margin_mm, right_margin_mm, bottom_margin_mm, left_margin_mm)
    for idx, row in enumerate(addresses):
        _start_new_page_if_needed(c, idx, per_page)
        _draw_label(c, row, boxes[_page_slot(idx, per_page)], sender_address, font_family)
    c.save()
