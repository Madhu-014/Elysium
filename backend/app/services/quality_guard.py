import re
from collections import Counter

from app.services.tokenizer import count_tokens

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
    "be",
    "this",
    "that",
    "it",
    "as",
    "at",
    "by",
    "from",
    "into",
    "very",
    "also",
}

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")
REQUIREMENT_MARKERS = (
    "focus",
    "provide",
    "include",
    "must",
    "do not",
    "keep",
    "concise",
    "summary",
)

MIN_RETENTION_BY_MODE = {
    "eco": 0.60,
    "balanced": 0.72,
    "high_quality": 0.88,
}

MAX_REDUCTION_BY_MODE = {
    "eco": 75.0,
    "balanced": 60.0,
    "high_quality": 35.0,
}


def _words(text: str) -> list[str]:
    return [
        w
        for w in re.findall(r"[a-zA-Z0-9_]+", text.lower())
        if w not in STOPWORDS and len(w) > 2
    ]


def _term_present(term: str, candidate_words: set[str]) -> bool:
    if term in candidate_words:
        return True
    if term.endswith("s") and term[:-1] in candidate_words:
        return True
    if (term + "s") in candidate_words:
        return True
    return False


def _core_terms(source: str) -> set[str]:
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    counts = Counter(_words(source))
    terms = {term for term, _ in counts.most_common(24)}

    for line in lines:
        lowered = line.lower()
        if LIST_ITEM_RE.match(line) or any(marker in lowered for marker in REQUIREMENT_MARKERS):
            terms.update(_words(line))

    return {term for term in terms if len(term) > 2}


def _term_coverage(source: str, candidate: str) -> float:
    terms = _core_terms(source)
    if not terms:
        return 1.0

    candidate_words = set(_words(candidate))
    covered = sum(1 for term in terms if _term_present(term, candidate_words))
    return covered / len(terms)


def _requirement_coverage(source: str, candidate: str) -> float:
    source_lines = [line.strip() for line in source.splitlines() if line.strip()]
    req_lines = []
    for line in source_lines:
        lowered = line.lower()
        if LIST_ITEM_RE.match(line) or any(marker in lowered for marker in REQUIREMENT_MARKERS):
            req_lines.append(line)

    if not req_lines:
        return 1.0

    candidate_words = set(_words(candidate))
    matched = 0
    for req in req_lines:
        req_terms = _words(req)
        if not req_terms:
            continue

        # Count a requirement as retained if at least half of its terms survive.
        covered = sum(1 for term in req_terms if _term_present(term, candidate_words))
        if covered / len(req_terms) >= 0.5:
            matched += 1

    return matched / len(req_lines)


def intent_retention_score(source: str, candidate: str) -> float:
    term_coverage = _term_coverage(source, candidate)
    req_coverage = _requirement_coverage(source, candidate)
    return round((term_coverage * 0.65) + (req_coverage * 0.35), 4)


def pick_context_safe_output(source: str, candidates: list[str], mode: str) -> str:
    if not source.strip():
        return ""

    before = count_tokens(source)
    if before <= 0:
        return source

    min_retention = MIN_RETENTION_BY_MODE[mode]
    max_reduction = MAX_REDUCTION_BY_MODE[mode]

    for candidate in candidates:
        cleaned = candidate.strip()
        if not cleaned:
            continue

        after = count_tokens(cleaned)
        reduction = ((before - after) / before) * 100 if before else 0
        score = intent_retention_score(source, cleaned)

        if score >= min_retention and reduction <= max_reduction:
            return cleaned

    return source
