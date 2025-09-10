# Debt Collection Call Analyzer: Final Technical Report

**Author:** Aryaman Gupta
**Date:** September 8, 2025
**Live Demo:** **[https://debt-call-analyst.streamlit.app/](https://debt-call-analyst.streamlit.app/)**

---

## 1. Executive Summary

This project was intentionally scoped to rapidly validate a deterministic, auditable system for debt collection compliance and quality monitoring. The work was not an academic exercise in model accuracy but a production-centric initiative to deliver immediate business value. We successfully engineered and deployed a complete solution, including an interactive Streamlit UI and a scalable batch-processing pipeline, in under eight focused hours.

The system delivers trustworthy, actionable flags for compliance violations and profanity, provides repeatable call-quality metrics (overtalk, silence), and establishes a clear, low-risk path for future ML/LLM augmentation. The final product is a strategic, minimum-viable compliance engine: rapid to deploy, auditable for legal review, and built to scale.

---

## 2. Project Overview

### Goal
The primary objective is to analyze conversations between debt collection agents and borrowers to identify and quantify key events related to compliance, professionalism, and conversational dynamics. The analysis focuses on three core areas:
1.  **Profanity Detection:** Identifying profane language used by both agents and borrowers.
2.  **Privacy/Compliance Violations:** Detecting instances where agents share sensitive account information before properly verifying the borrower's identity.
3.  **Call-Quality Metrics:** Calculating the percentage of overtalk (simultaneous speech) and silence within each call.

### Data Format
The input for the analysis consists of YAML/JSON files, where each file represents a single call. Each file contains a list of utterances, with each utterance defined by: `speaker`, `text`, `stime`, and `etime`.

---

## 3. Methodology & Strategic Design Choices

### 3.1. The "Deterministic by Design" Approach
A foundational strategic choice for this project was to prioritize an interpretable, regex-based engine over a "black box" ML model for the initial phase. This decision was made to maximize business trust, ensure 100% auditability for compliance teams, and deliver a production-ready baseline with speed and cost-efficiency. This approach also serves a secondary strategic goal: using the deterministic engine to produce a high-quality, labeled seed dataset to dramatically accelerate future ML/LLM development.

### 3.2. Profanity & Compliance Violation Detection
The detection logic is built on a time-based, pattern-matching algorithm.
-   **Profanity:** Utterances are normalized (lowercase, leetspeak mapping) and matched against an externalized list of regex patterns in `patterns/profanity_patterns.txt`.
-   **Compliance:** The system identifies timestamps for "Verification Cues" (e.g., `date of birth`, `SSN`) and "Disclosure Cues" (e.g., `balance`, `account number`). A violation is flagged if a disclosure occurs before a successful verification, providing a clear, rule-based audit trail.

### 3.3. Call-Quality Metrics
-   **Overtalk %:** Calculated by summing the duration of all overlapping speech intervals and dividing by the total call time. This is computed using a precise interval intersection algorithm to ensure accuracy.
-   **Silence %:** Calculated by finding the union of all speaking intervals to get total speech time, subtracting this from the total call duration, and dividing the result by the total call duration.

---

## 4. Key Architectural Decisions

To ensure the system was robust, maintainable, and user-friendly, we made several key architectural choices:

-   **Externalized Business Rules Engine:** Instead of hard-coding detection patterns, we store them in simple `.txt` files (`patterns/`). This crucial design choice decouples the business logic from the application code, empowering non-technical users in compliance to update rules without engineering intervention.
-   **Resilient Data Ingestion Pipeline:** Anticipating inconsistent data formats, we engineered a robust `io_json.py` loader. It handles both JSON and YAML, automatically coerces data types, and normalizes inputs, ensuring that a single malformed file will not halt a large batch-processing run.
-   **Modular, Extensible Codebase:** The project is structured with a clear separation of concerns (`io`, `metrics`, `detection`, `visualization`), making the system easy to maintain, test, and extend with future ML/LLM components.

---

## 5. Results & Visualization Analysis

The system successfully processes call data and outputs a comprehensive summary dashboard in the Streamlit application, with results also exportable to CSV/XLSX.

![Summary Dashboard](reports/SS1.JPG)
**Figure 1: Summary Dashboard.** The UI provides an at-a-glance overview of all processed calls, with color-coded flags for immediate identification of issues.

![Interactive Timeline](reports/SS2.JPG)
**Figure 2: Interactive Timeline.** For any given call, the timeline visualization provides a granular, second-by-second view of the conversation. Speaker utterances are shown as colored blocks, with overtalk highlighted in orange on the interrupting speaker and silence shown as gaps. This visual evidence is invaluable for agent coaching and dispute resolution.

---

## 6. Technical Challenges & Mitigation

The engineering process involved overcoming several real-world challenges to build a production-grade application:
-   **Challenge:** Inconsistent return types from detection functions causing pipeline failures.
    -   **Mitigation:** Enforced strict, guaranteed return schemas (always `dict` with expected keys) for all detector functions and added defensive checks in the batch processing script.
-   **Challenge:** Visualization libraries interpreting timestamps as epoch dates (1970), resulting in blank plots.
    -   **Mitigation:** Implemented a normalization layer to ensure all call timelines start at `t=0` and forced the plot axis to a linear scale, making the visuals robust and intuitive.
-   **Challenge:** Initial overtalk logic double-counting overlapping speech segments.
    -   **Mitigation:** Implemented a precise interval-merging algorithm to accurately calculate the union of speech intervals, ensuring defensible and auditable metrics.

---

## 7. Recommendations & Future Roadmap

This project has successfully established a high-trust foundation. The following next steps are recommended to build upon this momentum:

1.  **Phase 2: ML/LLM Integration:**
    -   Develop a prompt-based LLM classifier to run in parallel with the regex engine, focusing on detecting nuanced, context-dependent compliance risks.
    -   Use the regex engine's outputs as a seed dataset to fine-tune a supervised ML model, reducing annotation costs and accelerating development.
2.  **Enhanced Reporting & Operationalization:**
    -   Develop functionality to generate per-call PDF summary reports for compliance audits.
    -   Configure automated alerts (e.g., via Slack or email) for high-severity violations.
    -   Containerize the application with Docker for seamless deployment and set up a CI/CD pipeline for automated testing.

---

## 8. Conclusion

This project delivered a fully functional, production-ready compliance and quality analysis system. It successfully balances the immediate need for an auditable, deterministic tool with the strategic goal of creating a clean upgrade path to more advanced AI. The delivered assets—including the interactive Streamlit application and the scalable batch pipeline—provide immediate, tangible value and form a robust foundation for building a next-generation, data-driven call monitoring platform.