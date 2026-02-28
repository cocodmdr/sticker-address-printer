MM_TO_PT = 72 / 25.4

AVERY_TEMPLATES = {
    "L7160": {
        "rows": 7,
        "cols": 3,
        "label_width_mm": 63.5,
        "label_height_mm": 38.1,
        "pitch_x_mm": 66.7,
        "pitch_y_mm": 38.1,
        "origin_x_mm": 7.1,
        "origin_y_mm": 15.1,
    }
}


def avery_template(code: str):
    if code not in AVERY_TEMPLATES:
        raise ValueError(f"Unknown Avery template: {code}")
    return AVERY_TEMPLATES[code]


def mm_to_pt(mm: float) -> float:
    return mm * MM_TO_PT


def label_positions(template: dict, top_margin_mm=0.0, right_margin_mm=0.0, bottom_margin_mm=0.0, left_margin_mm=0.0):
    boxes = []
    for r in range(template["rows"]):
        for c in range(template["cols"]):
            x_mm = template["origin_x_mm"] + c * template["pitch_x_mm"] + left_margin_mm - right_margin_mm
            y_mm = template["origin_y_mm"] + r * template["pitch_y_mm"] + top_margin_mm - bottom_margin_mm
            boxes.append(
                (
                    mm_to_pt(x_mm),
                    mm_to_pt(y_mm),
                    mm_to_pt(template["label_width_mm"]),
                    mm_to_pt(template["label_height_mm"]),
                )
            )
    return boxes
