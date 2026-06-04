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
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bhelp me with\b",
    r"\bif you don't mind\b",
    r"\bi would appreciate it if\b",
]


def _clean_line(line: str, mode: str) -> str:
    cleaned = line.strip()
    if not cleaned:
        return ""

    # Keep explicit headers and numbered requirements intact.
    if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", cleaned) or cleaned.endswith(":"):
        return cleaned
        
    # Keep JSON-like syntax intact
    if cleaned in {"{", "}", "[", "]", "},", "],"} or '":' in cleaned:
        return cleaned

    if mode in {"eco-max", "optimal"}:
        patterns = list(COMMON_FILLER_PATTERNS)
        if mode == "eco-max":
            patterns.extend(ECO_EXTRA_FILLER_PATTERNS)

        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"([!?.,]){2,}", r"\1", cleaned)
    return cleaned.strip()


def _truncate_lines(lines: list[tuple[str, bool]], mode: str) -> list[str]:
    max_words = {"eco-max": 120, "optimal": 280, "precision": 1200}[mode]
    budget = max_words
    out: list[str] = []

    for line, is_protected in lines:
        words = line.split()
        if not words:
            continue
            
        if is_protected:
            out.append(line)
            budget -= len(words)
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
        
    lines_with_meta: list[tuple[str, bool]] = []
    in_code_block = False
    
    for raw_line in text.splitlines():
        if raw_line.strip().startswith("```"):
            in_code_block = not in_code_block
            lines_with_meta.append((raw_line.strip(), True))
            continue
            
        if in_code_block:
            lines_with_meta.append((raw_line, True))
        else:
            cleaned = _clean_line(raw_line, mode)
            if cleaned:
                # Protect lines ending with ? as they are usually the core question, and protect list items
                is_list_item = bool(re.match(r"^\s*(?:[-*]|\d+[.)])\s+", cleaned))
                is_protected = cleaned.endswith("?") or is_list_item
                lines_with_meta.append((cleaned, is_protected))

    if mode == "precision":
        return "\n".join(l[0] for l in lines_with_meta)

    truncated = _truncate_lines(lines_with_meta, mode)
    return "\n".join(truncated)
