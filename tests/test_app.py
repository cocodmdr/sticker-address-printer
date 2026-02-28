import io

from sticker_printer.web import create_app


def test_upload_csv_and_get_pdf():
    app = create_app()
    client = app.test_client()

    data = {
        "template": "L7160",
        "top_margin": "0",
        "right_margin": "0",
        "bottom_margin": "0",
        "left_margin": "0",
        "csv_file": (io.BytesIO(b"title,name,surname,address,country\nDr,Jane,Doe,1 Main St,NL\n"), "addresses.csv"),
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"


def test_homepage_lists_multiple_avery_templates():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "L7160" in body
    assert "L7161" in body


def test_preview_endpoint_renders_html_preview():
    app = create_app()
    client = app.test_client()

    data = {
        "template": "L7160",
        "top_margin": "0",
        "right_margin": "0",
        "bottom_margin": "0",
        "left_margin": "0",
        "csv_file": (io.BytesIO(b"title,name,surname,address,country\nDr,Jane,Doe,1 Main St,NL\n"), "addresses.csv"),
    }
    response = client.post("/preview", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "Preview" in response.get_data(as_text=True)


def test_sample_csv_download():
    app = create_app()
    client = app.test_client()

    response = client.get("/sample.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "title,name,surname,address,country" in response.get_data(as_text=True)
