from sticker_printer.web import create_app


def test_homepage_defaults_to_english():
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'Print address labels in minutes' in body


def test_homepage_supports_french():
    app = create_app()
    client = app.test_client()
    response = client.get('/?lang=fr')
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'Imprimez des étiquettes d\'adresse en quelques minutes' in body


def test_homepage_supports_dutch():
    app = create_app()
    client = app.test_client()
    response = client.get('/?lang=nl')
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'Print adreslabels in minuten' in body
