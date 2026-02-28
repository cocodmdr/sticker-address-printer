from sticker_printer.web import create_app


def test_homepage_has_marketing_sections_and_images():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Print address labels in minutes" in body
    assert "How it works" in body
    assert "templates preview" in body.lower()
    assert "/static/images/hero-labels.svg" in body
