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
    res = client.post('/preview-json', data=data, content_type='multipart/form-data')
    result = res.get_json()
    assert res.status_code == 200
    assert 'pdf_data_uri' in result
    assert result['pdf_data_uri'].startswith('data:application/pdf;base64,')
