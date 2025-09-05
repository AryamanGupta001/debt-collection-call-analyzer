# Technical Report – Debt Collection Call Analysis

## 1. Problem Understanding
The goal of this assignment was to analyze call transcripts between collection agents and borrowers.  
We were asked to evaluate **compliance, professionalism, and call metrics** through three main tasks:

- **Profanity Detection** – Identify calls where agent or borrower used profane language.  
- **Privacy & Compliance Violation** – Detect when agents disclosed sensitive financial information without verifying borrower identity.  
- **Call Quality Metrics** – Calculate overtalk (simultaneous speech) and silence percentages.  

Deliverables included both **programmatic outputs** (flags, metrics, visualizations) and a comparative analysis of regex vs. ML/LLM approaches.

---

## 2. Data Preprocessing
- Input files are JSON/YAML with fields: `speaker`, `text`, `stime`, `etime`.  
- Normalization steps applied:
  - Speaker labels standardized (`agent`, `borrower`).  
  - Timestamps parsed, corrected if swapped.  
  - Text normalized to lowercase for regex matching.  
- Final dataset → chronological list of utterances with clean metadata.

---

## 3. Detection Logic

### 3.1 Profanity Detection
- **Regex-based approach:** matched against curated profanity word list.  
- Flags:
  - `Agent Profanity` → Yes/No  
  - `Borrower Profanity` → Yes/No  
- Evidence: utterances, matched words, timestamps.

### 3.2 Compliance Violation
- **Regex-based approach:** detect disclosure of account/balance info.  
- Verified that an identity confirmation (DOB, SSN, address) occurred **before** disclosure.  
- Flags:
  - `Compliance Violation` → Yes/No  
- Evidence: ordering of verification vs disclosure, sample utterances.

### 3.3 Call Metrics
- **Overtalk %** = proportion of total time where agent & borrower overlap.  
- **Silence %** = proportion of time with no active speaker.  
- Output as percentages.

---

## 4. Comparative Analysis: Regex vs. ML/LLM

### Regex Approach
✅ Pros:
- Fast, lightweight, no training required.  
- Transparent/auditable (easy to explain why a flag was raised).  
- Works well on small datasets.  

❌ Cons:
- Brittle → misses paraphrases (“pay up” ≠ “balance”).  
- Needs constant updates to slang/patterns.  
- False positives if context not understood.

### ML Approach (traditional classifier)
- Requires labeled training data (manual annotation).  
- Could capture more subtle cases (indirect profanity, paraphrased compliance).  
- More robust once trained, but annotation overhead is heavy.  

### LLM Approach
- Pretrained models (e.g., GPT-like) can handle paraphrasing and semantic nuance.  
- Few-shot prompting can achieve good accuracy without full training.  
- ❌ Downsides: latency, cost, lack of full auditability.  

### Recommendation
- **Profanity Detection**: Regex is sufficient for production (clear keywords). LLM could reduce false negatives in slang but adds cost.  
- **Compliance Violation**: Regex can bootstrap, but ML/LLM better capture context/order. For production, combine regex for hard checks + ML for semantic context.  

---

## 5. Validation
- Tested regex rules against sample calls (3 JSON checkpoints).  
- Manually verified profanity and compliance matches.  
- Compared metrics (overtalk, silence) against manual timestamp inspection.  
- All results aligned with expectations.  

---

## 6. Limitations & Future Improvements
- Regex only detects exact matches → expand slang/phrases list.  
- No semantic understanding → add ML/LLM pipeline.  
- Silence/overtalk metrics assume perfect timestamps → could improve with audio alignment.  
- Could integrate active learning → flag uncertain cases for human review.

---

## 7. Instructions to Run

### Streamlit App
```bash
pip install -r requirements.txt
streamlit run app.py
