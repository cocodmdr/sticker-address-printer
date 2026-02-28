from sticker_printer.web import create_app


def test_preview_page_is_translated_in_french():
    app = create_app()
    client = app.test_client()
    data = {
        'lang': 'fr',
        'template': 'L7160',
        'csv_file': (__import__('io').BytesIO(b'title,name,surname,address,country\nDr,Jane,Doe,1 Main St,NL\n'), 'a.csv')
    }
    res = client.post('/preview', data=data, content_type='multipart/form-data')
    body = res.get_data(as_text=True)
    assert res.status_code == 200
    assert 'Prévisualisation' in body
    assert 'Retour' in body


def test_selected_language_button_is_active():
    app = create_app()
    client = app.test_client()
    body = client.get('/?lang=fr').get_data(as_text=True)
    assert 'href="/?lang=fr" class="btn secondary active"' in body
