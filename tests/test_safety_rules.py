from backend.utils.safety_rules import detect_red_flags, is_emergency


def test_detects_chest_pain():
    assert is_emergency("I have severe chest pain and can't breathe")


def test_no_false_positive_on_normal_query():
    assert not is_emergency("What are common causes of a mild headache?")


def test_returns_matched_phrases():
    flags = detect_red_flags("I think I'm having a stroke, face drooping badly")
    assert "stroke" in flags
    assert "face drooping" in flags
