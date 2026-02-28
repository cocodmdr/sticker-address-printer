from sticker_printer.web import create_app


def test_stylesheet_is_served():
    app = create_app()
    client = app.test_client()
    response = client.get('/static/styles.css')
    assert response.status_code == 200
    assert 'text/css' in response.mimetype


def test_hero_image_is_served():
    app = create_app()
    client = app.test_client()
    response = client.get('/static/images/hero-labels.svg')
    assert response.status_code == 200
    assert response.mimetype in ('image/svg+xml', 'text/xml')
