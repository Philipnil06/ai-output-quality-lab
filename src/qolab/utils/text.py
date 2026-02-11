import re
from typing import Iterable, List

WORD_RE = re.compile(r"\b\w+\b")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F900-\U0001F9FF]+"
)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def split_sentences(text: str) -> List[str]:
    parts = [s.strip() for s in SENTENCE_SPLIT_RE.split(text)]
    return [p for p in parts if p]


def average_sentence_length(text: str) -> float:
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    word_counts = [count_words(s) for s in sentences]
    return sum(word_counts) / len(word_counts)


def count_emojis(text: str) -> int:
    return len(EMOJI_RE.findall(text))


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    lower = text.lower()
    return any(p.lower() in lower for p in phrases)


def count_keyword_hits(text: str, keywords: Iterable[str]) -> int:
    lower = text.lower()
    return sum(1 for k in keywords if k.strip() and k.lower() in lower)


def has_bullets(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("- ") or stripped.startswith("•"):
            return True
    return False


QUESTION_CTA_PHRASES = [
    "what do you think",
    "how do you",
    "curious how others",
    "curious if",
    "would love to hear",
]


def has_audience_question(text: str) -> bool:
    lower = text.lower()
    if "?" in text and any(p in lower for p in QUESTION_CTA_PHRASES):
        return True
    # also treat a final question mark as a soft signal
    stripped = text.strip()
    return stripped.endswith("?")


AD_COPY_PHRASES = [
    "book a demo",
    "request a demo",
    "schedule a demo",
    "sign up today",
    "get started today",
    "limited time offer",
    "try it free",
    "start your free trial",
    "unlock",
    "supercharge",
    "game-changer",
    "revolutionary",
    "cutting-edge",
    "next-level",
    "boost your",
    "transform your",
    "drive predictable growth",
]


def looks_like_ad_copy(text: str) -> bool:
    lower = text.lower()
    if contains_any(lower, AD_COPY_PHRASES):
        return True
    # simple heuristic: many occurrences of "we" + product-y verbs
    if lower.count(" we ") >= 3 and contains_any(
        lower, ["offer", "customers", "pricing", "upgrade"]
    ):
        return True
    return False
