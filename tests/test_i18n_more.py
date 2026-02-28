from sticker_printer.web import create_app


def test_homepage_supports_spanish():
    app = create_app()
    client = app.test_client()
    response = client.get('/?lang=es')
    assert response.status_code == 200
    assert 'Imprime etiquetas de dirección en minutos' in response.get_data(as_text=True)


def test_homepage_supports_german():
    app = create_app()
    client = app.test_client()
    response = client.get('/?lang=de')
    assert response.status_code == 200
    assert 'Adressetiketten in Minuten drucken' in response.get_data(as_text=True)


def test_homepage_supports_italian():
    app = create_app()
    client = app.test_client()
    response = client.get('/?lang=it')
    assert response.status_code == 200
    assert 'Stampa etichette indirizzo in pochi minuti' in response.get_data(as_text=True)
