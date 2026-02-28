import io
import re

from sticker_printer.web import create_app


def test_homepage_has_dark_mode_toggle():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Dark mode" in body
    assert "toggle-theme" in body


def test_preview_rejects_non_csv_upload_with_clear_message():
    app = create_app()
    client = app.test_client()

    data = {
        "template": "L7160",
        "csv_file": (io.BytesIO(b"%PDF-1.4 fake"), "document.pdf"),
    }
    response = client.post("/preview", data=data, content_type="multipart/form-data")
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Please upload a CSV file" in body


def test_generate_uses_timestamped_filename_with_template():
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
    cd = response.headers.get("Content-Disposition", "")
    assert re.search(r'labels_L7160_\d{8}-\d{6}\.pdf', cd)


def test_generate_accepts_custom_template():
    app = create_app()
    client = app.test_client()

    data = {
        "template": "CUSTOM",
        "custom_rows": "2",
        "custom_cols": "2",
        "custom_label_width_mm": "90",
        "custom_label_height_mm": "60",
        "custom_pitch_x_mm": "95",
        "custom_pitch_y_mm": "65",
        "custom_origin_x_mm": "10",
        "custom_origin_y_mm": "10",
        "csv_file": (
            io.BytesIO(
                b"title,name,surname,address,country\nDr,Jane,Doe,1 Main St,NL\nMr,John,Smith,2 Main St,FR\n"
            ),
            "addresses.csv",
        ),
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
