# Profanity detection logic
# src/profanity.py
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from unittest import result
from .text_norm import normalize

def load_profanity_patterns(path: str = "patterns/profanity_patterns.txt"):
    patterns = []
    p = Path(path)
    if not p.exists():
        return []
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # compile per-line pattern; patterns may already be appropriate regex
        try:
            patterns.append(re.compile(line, re.IGNORECASE))
        except re.error:
            # fallback escape literal
            patterns.append(re.compile(re.escape(line), re.IGNORECASE))
    return patterns

PROFANITY_PATTERNS = load_profanity_patterns()

def detect_profanity(utterances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Returns summary dict:
      - agent_has, borrower_has (bool)
      - hits: list of entries with speaker, text, stime, etime, matched_patterns (list)
    """
    agent_has = False
    borrower_has = False
    hits = []
    for u in utterances:
        text = normalize(u.get('text', ''))
        matched = []
        for pat in PROFANITY_PATTERNS:
            if pat.search(text):
                matched.append(pat.pattern)
        if matched:
            s = u.get('speaker','').lower()
            if s == 'agent':
                agent_has = True
            elif s == 'borrower':
                borrower_has = True
            hits.append({
                'speaker': s,
                'text': u.get('text',''),
                'stime': float(u['stime']),
                'etime': float(u['etime']),
                'matches': matched
            })
    result = {
        'agent_has': agent_has,
        'borrower_has': borrower_has,
        'hits': hits
    }
    if not isinstance(result, dict):
        result = {"agent_has": False, "borrower_has": False, "hits": []}
    return result
