from sticker_printer.web import create_app


def test_homepage_contains_cookie_banner_elements_when_ga_enabled(monkeypatch):
    monkeypatch.setenv('GA_MEASUREMENT_ID', 'G-TEST123456')
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    body = response.get_data(as_text=True)

    assert 'id="cookie-banner"' in body
    assert 'id="cookie-accept"' in body
    assert 'id="cookie-reject"' in body
    assert 'initAnalytics' in body
