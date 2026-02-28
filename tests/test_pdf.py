from pathlib import Path
from pypdf import PdfReader

from sticker_printer.pdf_render import render_labels_pdf


def test_render_pdf(tmp_path: Path):
    addresses = [
        {"title": "Dr", "name": "Jane", "surname": "Doe", "address": "1 Main St", "country": "NL"},
        {"title": "", "name": "John", "surname": "Smith", "address": "2 Main St", "country": "FR"},
    ]
    out = tmp_path / "labels.pdf"
    render_labels_pdf(addresses, "L7160", str(out), 0, 0, 0, 0)
    reader = PdfReader(str(out))
    assert len(reader.pages) == 1
