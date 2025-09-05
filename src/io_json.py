# src/io_json.py
import json
import yaml
from typing import List, Dict, Any
from pathlib import Path

Utterance = Dict[str, Any]

def load_file(path_or_buffer) -> List[Utterance]:
    """
    Accepts:
      - Path or path string (reads file)
      - file-like object (has .read())
      - raw JSON/YAML string or bytes
    Returns: list of utterances sorted by stime.
    """
    raw = None

    if isinstance(path_or_buffer, (bytes, bytearray)):
        raw = path_or_buffer.decode('utf-8')

    elif isinstance(path_or_buffer, str):
        s = path_or_buffer.strip()
        if s.startswith('{') or s.startswith('['):  # treat as raw JSON/YAML
            raw = path_or_buffer
        else:
            raw = Path(path_or_buffer).read_text(encoding='utf-8')

    elif hasattr(path_or_buffer, "read"):
        raw = path_or_buffer.read()
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')

    else:
        raw = Path(path_or_buffer).read_text(encoding='utf-8')

    # parse JSON first, then YAML fallback
    try:
        data = json.loads(raw)
    except Exception:
        data = yaml.safe_load(raw)

    if isinstance(data, dict):
        for k in ['utterances', 'utterance', 'transcript', 'data', 'conversation']:
            if k in data and isinstance(data[k], list):
                data = data[k]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        raise ValueError("Unsupported data structure: expected list of utterances")

    cleaned = []
    for u in data:
        if not isinstance(u, dict):
            continue
        if 'stime' not in u or 'etime' not in u:
            continue
        try:
            st = float(u.get('stime', 0.0))
            et = float(u.get('etime', st))
        except Exception:
            continue
        if et < st:
            st, et = et, st
        u['stime'] = st
        u['etime'] = et
        sp = str(u.get('speaker', '')).strip().lower()
        if 'agent' in sp:
            u['speaker'] = 'agent'
        elif sp in ['customer', 'borrower', 'caller']:
            u['speaker'] = 'borrower'
        else:
            u['speaker'] = sp if sp else 'unknown'
        cleaned.append(u)

    cleaned.sort(key=lambda x: x['stime'])
    return cleaned
