from pathlib import Path


def test_dark_mode_sets_visible_heading_color():
    css = Path('static/styles.css').read_text()
    assert 'body.dark .hero h1' in css
