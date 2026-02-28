from pathlib import Path


def test_mobile_breakpoints_present():
    css = Path('static/styles.css').read_text(encoding='utf-8')
    assert '@media (max-width: 900px)' in css
    assert '@media (max-width: 640px)' in css
    assert '.actions .btn' in css
