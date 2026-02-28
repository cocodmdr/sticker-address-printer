from sticker_printer.web import create_app


def test_french_translates_form_labels_and_badges():
    app = create_app()
    client = app.test_client()
    body = client.get('/?lang=fr').get_data(as_text=True)

    assert 'Import CSV' not in body
    assert 'Modèles Avery' in body
    assert 'Format personnalisé' in body
    assert 'Export PDF' in body
    assert 'Modèle Avery' in body
    assert 'Fichier CSV' in body
    assert 'Marge haute (mm)' in body


def test_dark_mode_uses_solid_background():
    css = open('static/styles.css', encoding='utf-8').read()
    assert 'body.dark {' in css
    dark_block = css.split('body.dark {',1)[1].split('}',1)[0]
    assert 'gradient' not in dark_block.lower()


def test_sender_address_field_present():
    app = create_app()
    client = app.test_client()
    body = client.get('/?lang=en').get_data(as_text=True)
    assert 'Sender address (optional)' in body
    assert 'name="sender_address"' in body
