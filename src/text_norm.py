# Text normalization functions
# src/text_norm.py
import re

LEET_MAP = {
    '@': 'a', '$': 's', '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't'
}

def normalize(text: str) -> str:
    """Lowercase, map basic leetspeak, collapse whitespace, remove odd control chars."""
    if text is None:
        return ""
    t = str(text).lower()
    # map common leet chars
    for k, v in LEET_MAP.items():
        t = t.replace(k, v)
    # replace non-word separators that might hide swear letters with a single separator
    t = re.sub(r'[\u2000-\u206F\u2E00-\u2E7F\W_]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t
