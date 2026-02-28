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
