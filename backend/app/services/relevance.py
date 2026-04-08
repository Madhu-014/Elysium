import re
from collections import Counter

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
}

INSTRUCTION_HINTS = {
    "focus",
    "provide",
    "include",
    "summary",
    "executive",
    "professional",
    "concise",
    "example",
    "company",
    "optimize",
    "do not",
    "must",
    "task",
    "recap",
}

COURTESY_PREFIXES = (
    "hello",
    "thank you",
    "i really appreciate",
    "i am looking forward",
)

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")
CORE_TOPIC_MARKERS = (
    "executive summary",
    "renewable",
    "solar",
    "wind",
    "grid",
    "professional",
    "concise",
    "company",
    "example",
)


def _normalize_words(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def _is_structured_instruction(lines: list[str]) -> bool:
    bullet_like = 0
    for line in lines:
        if LIST_ITEM_RE.match(line):
            bullet_like += 1

    has_recap = any("recap" in line.lower() for line in lines)
    has_system_header = any("system instructions" in line.lower() for line in lines)
    return bullet_like >= 2 or has_recap or has_system_header


def _is_hard_requirement(sentence: str) -> bool:
    s = sentence.lower()
    if LIST_ITEM_RE.match(sentence):
        return True
    return any(
        marker in s
        for marker in (
            "focus on",
            "provide",
            "do not",
            "must",
            "to recap",
            "make sure",
            "keep the tone",
        )
    )


def _is_courtesy_line(line: str) -> bool:
    normalized = line.strip().lower()
    return any(normalized.startswith(prefix) for prefix in COURTESY_PREFIXES)


def _is_core_topic_sentence(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(marker in lowered for marker in CORE_TOPIC_MARKERS)


def _filter_structured_lines(lines: list[str], mode: str) -> list[str]:
    if mode == "high_quality":
        # Preserve high semantic fidelity while trimming social openers/closers.
        kept = [line for line in lines if not _is_courtesy_line(line)]
        return kept or lines

    recap_idx = next((idx for idx, line in enumerate(lines) if "to recap" in line.lower()), -1)
    recap_lines = lines[recap_idx:] if recap_idx >= 0 else []

    kept: list[str] = []

    if recap_lines:
        heading = [line for line in lines[:recap_idx] if line.endswith(":")][:1]
        numbered = [line for line in recap_lines if LIST_ITEM_RE.match(line)]

        context = [
            line
            for line in lines[:recap_idx]
            if "executive summary" in line.lower() or "renewable energy" in line.lower()
        ][:1]

        if mode == "eco":
            return (heading + context + ["To recap:"] + numbered) or recap_lines

        # Balanced retains recap items plus one high-level context sentence.
        return (heading + context + ["To recap:"] + numbered) or recap_lines

    for line in lines:
        lowered = line.lower()

        if _is_courtesy_line(line):
            continue

        if mode == "eco":
            # Keep only lines that carry concrete instructions or headings.
            if (
                _is_hard_requirement(line)
                or "executive summary" in lowered
                or "focus" in lowered
                or "solar" in lowered
                or "wind" in lowered
                or "grid" in lowered
                or "professional" in lowered
                or "concise" in lowered
                or "example" in lowered
                or "company" in lowered
                or line.endswith(":")
            ):
                kept.append(line)
            continue

        # Balanced mode: keep explicit constraints and core topic lines.
        if (
            _is_hard_requirement(line)
            or "executive summary" in lowered
            or "renewable energy" in lowered
            or "solar" in lowered
            or "wind" in lowered
            or "grid" in lowered
            or "professional" in lowered
            or "concise" in lowered
            or "company" in lowered
            or line.endswith(":")
        ):
            kept.append(line)

    if not kept:
        return lines

    return kept


def filter_relevant_sentences(text: str, mode: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) <= 2:
        return stripped

    # For structured prompts, preserve hierarchy but apply mode-aware pruning.
    if _is_structured_instruction(lines):
        return "\n".join(_filter_structured_lines(lines, mode))

    sentences = _sentence_split(stripped)
    if len(sentences) <= 2:
        return stripped

    doc_terms = Counter(_normalize_words(stripped))
    top_terms = {term for term, _count in doc_terms.most_common(18)}

    scored: list[tuple[int, int, str]] = []
    for idx, sentence in enumerate(sentences):
        sentence_terms = set(_normalize_words(sentence))
        overlap = len(sentence_terms & top_terms)
        hint_bonus = sum(1 for hint in INSTRUCTION_HINTS if hint in sentence.lower())
        req_bonus = 3 if _is_hard_requirement(sentence) else 0
        score = overlap + hint_bonus + req_bonus
        scored.append((score, idx, sentence))

    keep_ratio = {"eco": 0.55, "balanced": 0.7, "high_quality": 0.9}[mode]
    min_keep = {"eco": 2, "balanced": 3, "high_quality": 4}[mode]
    keep_count = min(len(sentences), max(int(len(sentences) * keep_ratio), min_keep))

    top_scored = sorted(scored, key=lambda item: (item[0], -item[1]), reverse=True)[:keep_count]
    keep_indices = {idx for _score, idx, _sentence in top_scored}

    # Always keep the opening context and explicit requirement sentences.
    keep_indices.add(0)
    for idx, sentence in enumerate(sentences):
        if _is_hard_requirement(sentence) or _is_core_topic_sentence(sentence):
            keep_indices.add(idx)

    kept = [sentence for idx, sentence in enumerate(sentences) if idx in keep_indices]
    return "\n".join(kept)
