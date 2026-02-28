import io

from sticker_printer.web import create_app


def test_preview_page_embeds_pdf_data_uri():
    app = create_app()
    client = app.test_client()

    data = {
        'lang': 'en',
        'template': 'L7160',
        'font_family': 'Helvetica',
        'csv_file': (io.BytesIO(b'title_line_1,title,name,surname,address,country\nVIP,Dr,Jane,Doe,1 Main St,NL\n'), 'a.csv')
    }
    res = client.post('/preview', data=data, content_type='multipart/form-data')
    body = res.get_data(as_text=True)
    assert res.status_code == 200
    assert 'id="pdf-preview"' in body
    assert 'data:application/pdf;base64,' in body
