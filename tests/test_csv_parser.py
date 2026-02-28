from sticker_printer.csv_parser import parse_addresses


def test_parse_addresses_with_title():
    csv_text = "title,name,surname,address,country\nDr,Jane,Doe,1 Main St,NL\n"
    rows = parse_addresses(csv_text)
    assert rows[0]["title"] == "Dr"
    assert rows[0]["name"] == "Jane"
    assert rows[0]["surname"] == "Doe"
    assert rows[0]["address"] == "1 Main St"
    assert rows[0]["country"] == "NL"
