from app.utils.borderline import detect_borderline_input


def test_messy_paste_detected_as_borderline():
    text = "remote work won. not sure if this is a thread worth writing tho kinda obvious?"
    r = detect_borderline_input(text)
    assert r.is_borderline
    assert r.critic_strictness_boost == 0.15
