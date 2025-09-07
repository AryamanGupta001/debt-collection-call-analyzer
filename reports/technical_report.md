# Debt Collection Call Compliance & Quality Analysis

**Author:** Aryaman Gupta

**Date:** September 6, 2025

---

## 2. Executive Summary

This project was designed to rapidly validate the feasibility of an automated compliance and quality analysis system for debt-collection calls, while uncovering key operational insights for future scaling. The delivered system combines a high-speed, deterministic regex-based detection engine for auditable compliance checks with advanced visual analytics for call-quality metrics. It successfully provides an interactive analysis application and a scalable batch-processing pipeline, establishing a strong, production-ready foundation for enterprise-grade monitoring and future integration of more complex Machine Learning models.

---

## 3. Project Overview

### Goal
The primary objective is to analyze conversations between debt collection agents and borrowers to identify and quantify key events related to compliance, professionalism, and conversational dynamics. The analysis focuses on three core areas:
1.  **Profanity Detection:** Identifying profane language used by both agents and borrowers.
2.  **Privacy/Compliance Violations:** Detecting instances where agents share sensitive account information before properly verifying the borrower's identity.
3.  **Call-Quality Metrics:** Calculating the percentage of overtalk (simultaneous speech) and silence within each call.

### Data Format
The input for the analysis consists of YAML files, where each file represents a single call recording. The structure of each file contains a list of utterances, with each utterance defined by:
-   **`speaker`**: `agent` or `borrower`
-   **`text`**: The transcribed content of the speech
-   **`stime`**: The start timestamp of the utterance in seconds
-   **`etime`**: The end timestamp of the utterance in seconds

---

## 4. Methodology

### 4.1 Profanity Detection

**Pattern Matching:**
A deterministic approach was implemented using a curated list of regular expressions (`regex`) stored in an external file (`profanity_patterns.txt`). The system first normalizes the utterance text (to lowercase, mapping leet-speak characters like `@` to `a`, `$` to `s`) before applying the regex patterns. This method provides high-speed, explicit, and fully auditable flagging of profane terms.

**ML/LLM Approach:**
A comparative design for a Machine Learning approach was conceptualized using a fine-tuned Large Language Model (LLM) prompt system. This method is designed to identify contextually inappropriate or coded language that a simple keyword match would miss, offering a more nuanced understanding of professionalism.

**Comparison:**
The regex approach is superior in speed, cost, and interpretability, making it ideal for flagging unambiguous violations. Its weakness is a lower recall for paraphrased or context-dependent profanity. The LLM approach excels at nuance and context but comes with higher computational costs and reduced transparency ("black box" problem), making it a powerful but secondary tool for deeper investigation.

### 4.2 Privacy & Compliance Violation Detection

**Pattern Matching:**
The core compliance rule—"verify before disclosing"—was implemented using a time-based regex algorithm. The system scans for two categories of cues:
1.  **Verification Cues:** Terms like `date of birth`, `last four`, `SSN`.
2.  **Disclosure Cues:** Terms like `balance`, `account number`, `total due`.
A violation is flagged if the earliest timestamp of a *disclosure cue* occurs before the earliest timestamp of a *verification cue*. This provides a clear, rule-based, and auditable result.

**ML/LLM Approach:**
The LLM-based design focuses on semantic understanding. It aims to detect "implied disclosures," where an agent might hint at sensitive information without using specific keywords (e.g., "Let's talk about the amount you've owed since May").

**Comparison:**
Pattern matching provides an invaluable, high-precision tool for enforcing explicit compliance rules. The LLM approach serves as a strategic enhancement to catch subtle, context-dependent violations that are not captured by rigid patterns.

### 4.3 Call-Quality Metrics

**Overtalk %:**
This metric quantifies simultaneous speech. It is calculated by identifying all time intervals where agent and borrower utterances overlap.
-   **Formula:** `(Total duration of all overlapping speech intervals / Total call duration) * 100`
-   **Logic:** The system builds lists of speech intervals for the agent and borrower, calculates the duration of their intersections, and sums them up.

**Silence %:**
This metric quantifies periods where neither party is speaking.
-   **Formula:** `(Total call duration - Total duration of all unique speaking intervals) / Total call duration * 100`
-   **Logic:** The system first creates a merged union of all speaking intervals to find the total time spent talking, then subtracts this from the total call duration.

**Visualisations:**
Results are visualized using a Plotly timeline chart that displays each speaker's utterances, with overlays highlighting periods of overtalk and silence. A pie chart also illustrates the agent vs. borrower talk-time share.

---

## 5. Results

The system successfully processes all call files and generates a comprehensive summary of findings. The output is available both as a visual report in the deployed Streamlit application and as batch exports in CSV/XLSX format. The key deliverable is an actionable dashboard that allows stakeholders to quickly assess call compliance and quality at a glance.

**Sample Summary Output:**

| Call ID      | Profanity (Agent) | Profanity (Borrower) | Privacy Violation | Overtalk % | Silence % |
| :----------- | :---------------- | :------------------- | :---------------- | :--------- | :-------- |
| `00be25b0`   | No                | No                   | No                | 2.1%       | 14.5%     |
| `019b9e97`   | No                | No                   | **Yes**           | 0.4%       | 1.0%      |
| `0914a991`   | **Yes**           | No                   | No                | 8.9%       | 7.3%      |
| `09353e1f`   | No                | **Yes**              | **Yes**           | 15.2%      | 4.6%      |

These results demonstrate the system's ability to flag critical events across multiple categories, providing a rich dataset for operational review and agent training.

---

## 6. Recommendations

**Profanity Detection:**
It is recommended to use a hybrid approach. The implemented **regex engine** should serve as the primary, real-time filter for explicit and unambiguous profanity due to its speed and auditability. An **LLM classifier** should be integrated as a secondary tool for deeper, offline analysis of calls flagged for review, allowing it to catch nuanced or coded language.

**Privacy Violations:**
Similarly, the deterministic **regex algorithm** is the recommended solution for enforcing the core "verify-before-disclose" rule. An **LLM system** should be developed in the next phase to run alongside it, specifically to identify conversations where agents imply sensitive information without using explicit keywords.

**Next Steps:**
1.  **ML Model Training:** Use the high-quality, labeled data generated by the regex engine to efficiently train and fine-tune a production-grade ML/LLM classifier.
2.  **Regex Pattern Expansion:** Engage with compliance teams to continuously expand the externalized pattern files with new terms and phrases.
3.  **Automated Reporting:** Develop functionality to generate per-call PDF reports for compliance audits and configure automated alerts for high-severity violations.

---

## 7. Conclusion

This sprint delivered a fully functional compliance analysis system, a robust comparative evaluation framework, and a suite of clear visual analytics—all packaged in a modular and extensible architecture. The project successfully proves the value of an automated monitoring tool and provides immediate, tangible assets for the compliance and quality assurance teams. The next phase will focus on scaling the system's detection intelligence and integrating its outputs into daily operational workflows.

---

## 8. References

The implementation of this project relied on the following core Python libraries and frameworks:
-   **Streamlit:** For building and deploying the interactive web application.
-   **Pandas:** For data manipulation and aggregation.
-   **Plotly:** For generating interactive timeline visualizations and charts.
-   **PyYAML:** For parsing the input YAML call files.