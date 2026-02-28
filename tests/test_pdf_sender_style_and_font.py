from pathlib import Path
from pypdf import PdfReader

from sticker_printer.pdf_render import render_labels_pdf


def test_sender_address_rendered_and_font_selectable(tmp_path: Path):
    addresses = [
        {"title_line_1": "VIP", "title": "Dr", "name": "Jane", "surname": "Doe", "address": "1 Main St", "country": "NL"},
    ]
    out = tmp_path / 'labels.pdf'
    render_labels_pdf(addresses, 'L7160', str(out), sender_address='Sender Name', font_family='Courier')
    text = PdfReader(str(out)).pages[0].extract_text() or ''
    assert 'Sender Name' in text
    assert 'VIP' in text
