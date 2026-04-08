import re

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    if not text:
        return 0

    if tiktoken is not None:
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    # Fallback approximation if tokenizer package is unavailable.
    words = re.findall(r"\S+", text)
    return int(len(words) * 1.33)
