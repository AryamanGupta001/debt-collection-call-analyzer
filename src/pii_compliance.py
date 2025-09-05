# Privacy & Compliance violation detection
# src/pii_compliance.py
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from unittest import result
from .text_norm import normalize

def load_pii_patterns(path="patterns/pii_patterns.txt"):
    pats = []
    p = Path(path)
    if not p.exists():
        return []
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            pats.append(re.compile(line, re.IGNORECASE))
        except re.error:
            pats.append(re.compile(re.escape(line), re.IGNORECASE))
    return pats

PII_PATTERNS = load_pii_patterns()

# split PII patterns into categories roughly: verification vs disclosure
VERIFY_KEYWORDS = [
    re.compile(r'\b(date of birth|dob|d\.o\.b\.?)\b', re.IGNORECASE),
    re.compile(r'\b(verify|confirm).*(identity|dob|address|ssn|social security)', re.IGNORECASE),
    re.compile(r'\b(please confirm|can you confirm|for security reasons|for verification)\b', re.IGNORECASE),
    re.compile(r'\b(address|mailing address|street|apt|unit)\b', re.IGNORECASE),
    re.compile(r'\b(last four|last 4|(social security|ssn))\b', re.IGNORECASE),
]

DISCLOSE_KEYWORDS = [
    re.compile(r'\b(balance|outstanding|amount owed|total due|due amount|current balance)\b', re.IGNORECASE),
    re.compile(r'\b(account (number|no|id)|acct\.?\s*no\.?)\b', re.IGNORECASE),
    re.compile(r'\b(credit card|card number|cvv|expiration date)\b', re.IGNORECASE),
    re.compile(r'\b(transaction id|txn id|payment of|payment has been processed)\b', re.IGNORECASE),
]

def _first_time(utterances: List[Dict[str, Any]], patterns: List[re.Pattern], who: Optional[str]=None) -> Optional[float]:
    tmin = None
    for u in utterances:
        if who and u.get('speaker','').lower() != who:
            continue
        txt = normalize(u.get('text',''))
        for p in patterns:
            if p.search(txt):
                st = float(u['stime'])
                if tmin is None or st < tmin:
                    tmin = st
                break
    return tmin

def detect_compliance_violation(utterances: List[Dict[str, Any]], strict=False) -> Dict[str, Any]:
    """
    Returns:
      - violation: bool
      - evidence: dict with times and example utterances
    Logic:
      - find earliest agent disclosure (DISCLOSE_KEYWORDS from agent)
      - find earliest verification (agent request OR borrower confirmation)
      - violation if disclosure occurs before verification or if disclosure exists and no verification found
    strict: if True, require borrower confirmation after agent's request to count verification
    """
    disclose_time = _first_time(utterances, DISCLOSE_KEYWORDS, who='agent')
    # agent verification requests
    verify_agent_time = _first_time(utterances, VERIFY_KEYWORDS, who='agent')
    # borrower confirmations could also be in verify patterns (like dates, numbers); treat borrower as confirm
    verify_borrower_time = _first_time(utterances, VERIFY_KEYWORDS, who='borrower')

    verify_time = None
    if strict:
        if verify_agent_time is not None and verify_borrower_time is not None and verify_borrower_time >= verify_agent_time:
            verify_time = verify_borrower_time
    else:
        verify_time = verify_agent_time if verify_agent_time is not None else verify_borrower_time

    violation = False
    reason = None
    if disclose_time is not None:
        if verify_time is None or disclose_time < verify_time:
            violation = True
            if verify_time is None:
                reason = "Disclosure occurred and no prior verification detected."
            else:
                reason = f"Disclosure at {disclose_time:.2f}s before verification at {verify_time:.2f}s."

    # collect evidence utterances (examples)
    evidence = {'disclose_time': disclose_time, 'verify_time': verify_time, 'reason': reason}
    examples = []
    for u in utterances:
        st = float(u['stime'])
        txt = u.get('text','')
        if disclose_time is not None and abs(st - disclose_time) < 1e-6:
            examples.append({'type': 'disclose', 'speaker': u['speaker'], 'text': txt, 'stime': st})        
        if verify_time is not None and abs(st - verify_time) < 1e-6:
            examples.append({'type': 'verify', 'speaker': u['speaker'], 'text': txt, 'stime': st})
    evidence['examples'] = examples
    result = {'violation': violation, 'evidence': evidence}
    if not isinstance(result, dict):
        result = {"violation": False, "evidence": {}}
    return result


