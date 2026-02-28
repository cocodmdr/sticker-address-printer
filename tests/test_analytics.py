import os

from sticker_printer.web import create_app


def test_homepage_has_no_analytics_by_default(monkeypatch):
    monkeypatch.delenv('GA_MEASUREMENT_ID', raising=False)
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    body = response.get_data(as_text=True)
    assert 'googletagmanager.com/gtag/js' not in body


def test_homepage_injects_ga_when_configured(monkeypatch):
    monkeypatch.setenv('GA_MEASUREMENT_ID', 'G-TEST123456')
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    body = response.get_data(as_text=True)
    assert 'googletagmanager.com/gtag/js?id=G-TEST123456' in body
    assert "gtag('config', 'G-TEST123456')" in body
