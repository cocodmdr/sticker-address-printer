from sticker_printer.layout import avery_template, label_positions


def test_avery_l7160_shape():
    tpl = avery_template("L7160")
    assert tpl["rows"] == 7
    assert tpl["cols"] == 3


def test_label_positions_count():
    tpl = avery_template("L7160")
    boxes = label_positions(tpl, top_margin_mm=0, right_margin_mm=0, bottom_margin_mm=0, left_margin_mm=0)
    assert len(boxes) == tpl["rows"] * tpl["cols"]
