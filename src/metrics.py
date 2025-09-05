# Overtalk and Silence metrics
# src/metrics.py
from typing import List, Dict, Tuple
from math import isclose

def call_bounds(utterances: List[Dict]) -> Tuple[float, float]:
    if not utterances:
        return (0.0, 0.0)
    s0 = min(float(u['stime']) for u in utterances)
    e1 = max(float(u['etime']) for u in utterances)
    return s0, e1

def merge_intervals(intervals):
    """Merge overlapping intervals. intervals: list of (s,e) floats."""
    ivs = [(float(s), float(e)) for s,e in intervals if e > s]
    ivs.sort()
    merged = []
    for s,e in ivs:
        if not merged:
            merged.append([s,e])
        else:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s,e])
    return [(s,e) for s,e in merged]

def duration(intervals):
    return sum((e-s) for s,e in intervals)

def overtalk_percentage(utterances: List[Dict]) -> float:
    agents = [(float(u['stime']), float(u['etime'])) for u in utterances if u.get('speaker','').lower()=='agent']
    borrowers = [(float(u['stime']), float(u['etime'])) for u in utterances if u.get('speaker','').lower()=='borrower']
    i,j = 0,0
    overlaps = []
    agents.sort()
    borrowers.sort()
    while i < len(agents) and j < len(borrowers):
        a_s,a_e = agents[i]
        b_s,b_e = borrowers[j]
        s = max(a_s, b_s)
        e = min(a_e, b_e)
        if e > s and not (isclose(e,s)):
            overlaps.append((s,e))
        # advance pointer with earlier end
        if a_e <= b_e:
            i += 1
        else:
            j += 1
    merged = merge_intervals(overlaps)
    s0, e1 = call_bounds(utterances)
    call_len = max(1e-9, e1 - s0)
    return (duration(merged) / call_len) * 100.0

def silence_percentage(utterances: List[Dict]) -> float:
    intervals = [(float(u['stime']), float(u['etime'])) for u in utterances]
    merged = merge_intervals(intervals)
    speaking = duration(merged)
    s0,e1 = call_bounds(utterances)
    call_len = max(1e-9, e1 - s0)
    silence = max(0.0, call_len - speaking)
    return (silence / call_len) * 100.0

def talk_share(utterances):
    """Return total call duration (s), agent % talk, borrower % talk."""
    if not utterances:
        return {"total": 0.0, "agent_pct": 0.0, "borrower_pct": 0.0}

    total = max(u.get("etime", 0.0) for u in utterances)

    agent_time = sum(
        max(0.0, float(u.get("etime", 0.0)) - float(u.get("stime", 0.0)))
        for u in utterances if u.get("speaker", "").lower() == "agent"
    )

    borrower_time = sum(
        max(0.0, float(u.get("etime", 0.0)) - float(u.get("stime", 0.0)))
        for u in utterances if u.get("speaker", "").lower() == "borrower"
    )

    if total <= 0:
        return {"total": 0.0, "agent_pct": 0.0, "borrower_pct": 0.0}

    return {
        "total": total,
        "agent_pct": agent_time / total * 100,
        "borrower_pct": borrower_time / total * 100
    }
