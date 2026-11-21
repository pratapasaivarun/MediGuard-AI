from evaluation.run_all import normalize_line_item_description


def test_line_item_description_normalization_ignores_parenthetical_acronyms():
    expected = "Complete blood count (CBC) laboratory test"
    extracted = "Complete blood count laboratory test"

    assert normalize_line_item_description(expected) == normalize_line_item_description(extracted)
