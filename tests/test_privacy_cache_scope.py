from sticker_printer.web import create_app


def test_sensitive_cache_uses_session_storage_not_local_storage():
    app = create_app()
    client = app.test_client()
    body = client.get('/').get_data(as_text=True)
    assert 'sessionStorage.setItem(\'csv_text_cache\'' in body
    assert 'sessionStorage.setItem(\'sender_address_cache\'' in body
    assert 'localStorage.setItem(\'csv_text_cache\'' not in body
