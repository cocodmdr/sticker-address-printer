import io

from sticker_printer.web import create_app


def test_preview_accepts_cp1252_encoded_csv():
    app = create_app()
    client = app.test_client()

    csv_text = "title,name,surname,address,country\nDr,André,Doe,1 Rue de l'Église,FR\n"
    data = {
        "template": "L7160",
        "top_margin": "0",
        "right_margin": "0",
        "bottom_margin": "0",
        "left_margin": "0",
        "csv_file": (io.BytesIO(csv_text.encode("cp1252")), "addresses.csv"),
    }
    response = client.post("/preview", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "Preview" in response.get_data(as_text=True)
