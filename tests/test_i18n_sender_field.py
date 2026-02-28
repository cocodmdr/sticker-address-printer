from sticker_printer.web import create_app


def test_french_sender_label_is_french_not_italian():
    app = create_app()
    client = app.test_client()
    body = client.get('/?lang=fr').get_data(as_text=True)
    assert 'Adresse expéditeur (optionnel)' in body
    assert 'Indirizzo mittente' not in body


def test_sender_placeholder_has_no_literal_backslash_n():
    app = create_app()
    client = app.test_client()
    body = client.get('/?lang=fr').get_data(as_text=True)
    assert '\\n' not in body
