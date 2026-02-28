from sticker_printer.web import create_app


def test_font_selector_present_on_homepage():
    app = create_app()
    client = app.test_client()
    body = client.get('/').get_data(as_text=True)
    assert 'name="font_family"' in body
    assert 'Helvetica' in body
    assert 'Courier' in body
