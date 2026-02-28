from pathlib import Path
from pypdf import PdfReader

from sticker_printer.pdf_render import render_labels_pdf


def test_render_pdf_uses_per_address_title_line_1(tmp_path: Path):
    addresses = [
        {
            "title_line_1": "INVITATION",
            "title": "Dr",
            "name": "Jane",
            "surname": "Doe",
            "address": "1 Main St",
            "country": "NL",
        },
    ]
    out = tmp_path / 'labels.pdf'
    render_labels_pdf(addresses, 'L7160', str(out))
    text = PdfReader(str(out)).pages[0].extract_text() or ''
    assert 'INVITATION' in text


def test_render_pdf_includes_sender_address_block(tmp_path: Path):
    addresses = [
        {"title": "Dr", "name": "Jane", "surname": "Doe", "address": "1 Main St", "country": "NL"},
    ]
    out = tmp_path / 'labels.pdf'
    render_labels_pdf(addresses, 'L7160', str(out), sender_address='Tyrex\n12 Dino Street\nThe Hague')
    text = PdfReader(str(out)).pages[0].extract_text() or ''
    assert 'Tyrex' in text
