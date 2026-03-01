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
    },
    "L7161": {
        "rows": 6,
        "cols": 3,
        "label_width_mm": 63.5,
        "label_height_mm": 46.6,
        "pitch_x_mm": 66.7,
        "pitch_y_mm": 46.6,
        "origin_x_mm": 7.1,
        "origin_y_mm": 19.0,
    },
    "L7163": {
        "rows": 7,
        "cols": 2,
        "label_width_mm": 99.1,
        "label_height_mm": 38.1,
        "pitch_x_mm": 101.6,
        "pitch_y_mm": 38.1,
        "origin_x_mm": 8.5,
        "origin_y_mm": 15.1,
    },
}

_TEMPLATE_KEYS = {
    "rows",
    "cols",
    "label_width_mm",
    "label_height_mm",
    "pitch_x_mm",
    "pitch_y_mm",
    "origin_x_mm",
    "origin_y_mm",
}


def avery_template(code: str):
    if code not in AVERY_TEMPLATES:
        raise ValueError(f"Unknown Avery template: {code}")
    return AVERY_TEMPLATES[code]


def _missing_template_keys(spec: dict) -> set[str]:
    return _TEMPLATE_KEYS - set(spec.keys())


def _validate_rows_cols(spec: dict):
    if int(spec["rows"]) <= 0 or int(spec["cols"]) <= 0:
        raise ValueError("Rows and columns must be > 0")


def validate_template_spec(spec: dict):
    missing = _missing_template_keys(spec)
    if missing:
        raise ValueError(f"Missing template fields: {', '.join(sorted(missing))}")
    _validate_rows_cols(spec)
    return spec


def list_avery_templates():
    return sorted(AVERY_TEMPLATES.keys())


def mm_to_pt(mm: float) -> float:
    return mm * MM_TO_PT


def _cell_xy_mm(template: dict, r: int, c: int, top: float, right: float, bottom: float, left: float) -> tuple[float, float]:
    x = float(template["origin_x_mm"]) + c * float(template["pitch_x_mm"]) + left - right
    y = float(template["origin_y_mm"]) + r * float(template["pitch_y_mm"]) + top - bottom
    return x, y


def _box_from_mm(template: dict, x_mm: float, y_mm: float) -> tuple[float, float, float, float]:
    return mm_to_pt(x_mm), mm_to_pt(y_mm), mm_to_pt(float(template["label_width_mm"])), mm_to_pt(float(template["label_height_mm"]))


def label_positions(template: dict, top_margin_mm=0.0, right_margin_mm=0.0, bottom_margin_mm=0.0, left_margin_mm=0.0):
    boxes = []
    for r in range(int(template["rows"])):
        for c in range(int(template["cols"])):
            x_mm, y_mm = _cell_xy_mm(template, r, c, top_margin_mm, right_margin_mm, bottom_margin_mm, left_margin_mm)
            boxes.append(_box_from_mm(template, x_mm, y_mm))
    return boxes
