from sticker_printer.web import create_app


def test_security_headers_present():
    app = create_app()
    client = app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'
    assert res.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert 'default-src' in (res.headers.get('Content-Security-Policy') or '')
