from qolab.evaluation.heuristics import (
    score_length_fit,
    score_brand_voice,
    score_structure,
)


def test_length_fit_within_bounds():
    text = "word " * 100
    assert score_length_fit(text, min_words=90, max_words=110) == 5


def test_length_fit_too_short():
    text = "word " * 40
    score = score_length_fit(text, min_words=90, max_words=110)
    assert 0 <= score < 5


def test_length_fit_too_long():
    text = "word " * 200
    score = score_length_fit(text, min_words=90, max_words=110)
    assert 0 <= score < 5


def test_brand_voice_banned_phrase_and_punctuation():
    text = "This is a revolutionary game-changer!!! 🚀"
    score = score_brand_voice(
        text,
        banned_phrases=["game-changer", "revolutionary"],
        max_emojis=0,
        max_exclamations=1,
    )
    assert score < 5


def test_structure_bullet_detection_and_cta():
    text = (
        "Hook sentence here.\n\n"
        "- Bullet one\n"
        "- Bullet two\n\n"
        "Book a demo to learn more."
    )
    score = score_structure(text, cta_phrases=["book a demo"])
    assert score == 5

