from __future__ import annotations

from typing import Dict, Iterable

from ..utils.text import (
    average_sentence_length,
    count_emojis,
    count_keyword_hits,
    count_words,
    has_bullets,
    contains_any,
    has_audience_question,
    looks_like_ad_copy,
)


def score_length_fit(text: str, min_words: int, max_words: int) -> int:
    words = count_words(text)
    if min_words <= words <= max_words:
        return 5
    if words == 0:
        return 0
    if words < min_words:
        ratio = words / max(min_words, 1)
    else:
        ratio = max_words / words if words > 0 else 0
    if ratio >= 0.8:
        return 4
    if ratio >= 0.6:
        return 3
    if ratio >= 0.4:
        return 2
    if ratio >= 0.2:
        return 1
    return 0


def score_structure(text: str, cta_phrases: Iterable[str]) -> int:
    score = 0
    sentences = text.split(".")
    hook = ".".join(sentences[:2])
    hook_words = count_words(hook)
    if 5 <= hook_words <= 35:
        score += 3
    if has_audience_question(text) or contains_any(text, cta_phrases):
        score += 2
    # bullets are no longer required; do not reward or penalize directly
    return min(score, 5)


def score_keyword_coverage(text: str, keywords: Iterable[str]) -> int:
    keywords = [k for k in keywords if k.strip()]
    if not keywords:
        return 0
    hits = count_keyword_hits(text, keywords)
    coverage = hits / len(keywords)
    if coverage >= 0.8:
        return 5
    if coverage >= 0.6:
        return 4
    if coverage >= 0.4:
        return 3
    if coverage >= 0.2:
        return 2
    if coverage > 0:
        return 1
    return 0


def score_clarity(text: str) -> int:
    avg_len = average_sentence_length(text)
    if avg_len == 0:
        return 0
    if avg_len <= 20:
        return 5
    if avg_len <= 25:
        return 4
    if avg_len <= 30:
        return 3
    if avg_len <= 35:
        return 2
    if avg_len <= 45:
        return 1
    return 0


def score_repetition(text: str) -> int:
    words = text.lower().split()
    if len(words) < 3:
        return 5
    trigrams = []
    for i in range(len(words) - 2):
        trigrams.append(" ".join(words[i : i + 3]))
    unique = len(set(trigrams))
    if not trigrams:
        return 5
    ratio = unique / len(trigrams)
    if ratio >= 0.9:
        return 5
    if ratio >= 0.8:
        return 4
    if ratio >= 0.7:
        return 3
    if ratio >= 0.6:
        return 2
    if ratio >= 0.4:
        return 1
    return 0


def score_brand_voice(
    text: str,
    banned_phrases: Iterable[str],
    max_emojis: int,
    max_exclamations: int,
    prefer_first_person: bool = False,
    avoid_salesy_ad_copy: bool = False,
) -> int:
    score = 5
    if contains_any(text, banned_phrases):
        score -= 2
    emojis = count_emojis(text)
    if emojis > max_emojis:
        score -= 1
    exclamations = text.count("!")
    if exclamations > max_exclamations:
        score -= 1
    lower = text.lower()
    if prefer_first_person and " i " not in f" {lower} " and " my " not in f" {lower} ":
        score -= 1
    if avoid_salesy_ad_copy and looks_like_ad_copy(text):
        score -= 2
    return max(score, 0)


def evaluate_heuristics(
    text: str,
    constraints: Dict,
    keywords: Iterable[str],
    cta_phrases: Iterable[str],
) -> Dict[str, int | float]:
    length_score = score_length_fit(text, constraints["min_words"], constraints["max_words"])
    structure_score = score_structure(text, cta_phrases)
    keyword_score = score_keyword_coverage(text, keywords)
    clarity_score = score_clarity(text)
    repetition_score = score_repetition(text)
    brand_score = score_brand_voice(
        text,
        constraints.get("banned_phrases", []),
        constraints.get("max_emojis", 0),
        constraints.get("max_exclamation_marks", 1),
        constraints.get("prefer_first_person", False),
        constraints.get("avoid_salesy_ad_copy", False),
    )
    total = (
        length_score
        + structure_score
        + keyword_score
        + clarity_score
        + repetition_score
        + brand_score
    )
    return {
        "length_fit": length_score,
        "structure": structure_score,
        "keyword_coverage": keyword_score,
        "clarity": clarity_score,
        "repetition": repetition_score,
        "brand_voice": brand_score,
        "total_heuristics": total,
    }
