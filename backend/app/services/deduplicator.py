def deduplicate_lines(text: str, mode: str = "balanced") -> str:
    result: list[str] = []

    if mode == "high_quality":
        # Conservative dedup: only collapse immediate duplicate lines.
        last_key = ""
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            key = line.lower()
            if key == last_key:
                continue
            result.append(line)
            last_key = key
        return "\n".join(result)

    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(line)

    return "\n".join(result)
