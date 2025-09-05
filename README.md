# Debt-Collection Call Analyzer (Regex baseline)

## What this repo provides
- Regex-based detectors for profanity and privacy/compliance violations.
- Call quality metrics: overtalk % and silence %.
- Streamlit UI to upload calls, run checks and visualize.
- CLI batch runner to process a directory of JSON/YAML calls and output CSV.

## Setup
1. `python -m venv .venv`
2. Activate `.venv`
3. `pip install -r requirements.txt`
4. `streamlit run app.py` (for UI) OR `python run_batch.py --input_dir ./data --output out.csv --entity pii`

## Tuning
- Edit `patterns/profanity_patterns.txt` and `patterns/pii_patterns.txt` to add domain-specific tokens, slang, and rules.
- Toggle strict verification mode in the UI to require borrower confirmation.

## Notes
- This is a *regex-first* baseline: deterministic, auditable, and fast.
- Consider adding an LLM classification step later to capture paraphrases and nuanced scenarios.
