import re

COMMON_FILLER_PATTERNS = [
    r"\bkindly\b",
    r"\bi would like you to\b",
    r"\bjust\b",
    r"\bbasically\b",
]

ECO_EXTRA_FILLER_PATTERNS = [
    r"\bi am looking for\b",
    r"\bi need\b",
    r"\bplease\b",
]


def _clean_line(line: str, mode: str) -> str:
    cleaned = line.strip()
    if not cleaned:
        return ""

    # Keep explicit headers and numbered requirements intact.
    if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", cleaned) or cleaned.endswith(":"):
        return cleaned

    if mode in {"eco", "balanced"}:
        patterns = list(COMMON_FILLER_PATTERNS)
        if mode == "eco":
            patterns.extend(ECO_EXTRA_FILLER_PATTERNS)

        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"([!?.,]){2,}", r"\1", cleaned)
    return cleaned.strip()


def _truncate_lines(lines: list[str], mode: str) -> list[str]:
    max_words = {"eco": 220, "balanced": 420, "high_quality": 1200}[mode]
    budget = max_words
    out: list[str] = []

    for line in lines:
        words = line.split()
        if not words:
            continue

        if len(words) <= budget:
            out.append(line)
            budget -= len(words)
            continue

        if budget > 12:
            out.append(" ".join(words[:budget]))
        break

    return out


def compress_prompt(text: str, mode: str) -> str:
    if not text.strip():
        return ""

    lines = [_clean_line(line, mode) for line in text.splitlines()]
    lines = [line for line in lines if line]

    if mode == "high_quality":
        return "\n".join(lines)

    truncated = _truncate_lines(lines, mode)
    return "\n".join(truncated)
