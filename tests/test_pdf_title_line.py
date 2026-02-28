from pathlib import Path
from pypdf import PdfReader

from sticker_printer.pdf_render import render_labels_pdf


def test_render_pdf_includes_global_title_line(tmp_path: Path):
    addresses = [
        {"title": "Dr", "name": "Jane", "surname": "Doe", "address": "1 Main St", "country": "NL"},
    ]
    out = tmp_path / 'labels.pdf'
    render_labels_pdf(addresses, 'L7160', str(out), global_title_line='INVITATION')
    text = PdfReader(str(out)).pages[0].extract_text() or ''
    assert 'INVITATION' in text
