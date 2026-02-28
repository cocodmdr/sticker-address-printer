import io

from sticker_printer.web import create_app


def test_preview_list_displays_title_line_1_when_present():
    app = create_app()
    client = app.test_client()

    data = {
        'lang': 'fr',
        'template': 'L7160',
        'font_family': 'Helvetica',
        'csv_file': (io.BytesIO(b'title_line_1,title,name,surname,address,country\nINVITATION,Dr,Jane,Doe,1 Main St,NL\n,Mr,John,Smith,2 River Rd,FR\n'), 'a.csv')
    }
    res = client.post('/preview', data=data, content_type='multipart/form-data')
    body = res.get_data(as_text=True)

    assert res.status_code == 200
    assert 'INVITATION' in body
    assert 'Dr Jane Doe — 1 Main St — NL' in body
