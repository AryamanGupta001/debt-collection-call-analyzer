# Debt Collection Call Analyzer: A Framework for Compliance and Quality Assurance

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

This project delivers a robust, end-to-end framework for the automated analysis of debt collection call transcripts. It provides actionable intelligence for compliance teams, quantifiable metrics for quality assurance, and a scalable architecture for future enhancements.

The system features an interactive web application for single-call diagnostics and a powerful command-line tool for batch processing thousands of calls, transforming raw call data into clear, auditable insights.

**Live Demo:** **[https://debt-call-analyst.streamlit.app/](https://debt-call-analyst.streamlit.app/)**

![App Screenshot](https://i.imgur.com/your-screenshot-url.png) <!-- It is highly recommended to add a screenshot of your Streamlit app here -->

---

## Key Features & Strategic Assets

*   **Interactive Diagnostic UI:** A deployed Streamlit application provides a user-friendly interface to upload single or multiple call files (including ZIP archives) and receive instant visual analysis.
*   **Scalable Batch Processing Engine:** A CLI script (`run_batch.py`) processes entire directories of call data, generating executive-ready summaries and detailed evidence logs in both **CSV** and **XLSX** formats.
*   **Maintainable Business Rules Engine:** Compliance and profanity rules are stored in external text files (`patterns/`). This strategic design allows non-technical users (e.g., compliance officers) to update detection logic without any code changes.
*   **Auditable Compliance Detection:** The system implements a time-based algorithm to flag a critical violation: disclosing sensitive information *before* borrower identity verification. All findings are supported by utterance-level evidence.
*   **Quantitative Call Quality Metrics:** Moves quality assurance from subjective to objective by calculating:
    *   **Overtalk %:** Percentage of the call where both parties are speaking simultaneously.
    *   **Silence %:** Percentage of the call with no speech.
    *   **Talk-Share %:** The ratio of talk time between the agent and the borrower.
*   **High-Fidelity Visualizations:** Each call is rendered as an interactive timeline chart showing speaker activity, highlighting overtalk interruptions and silence periods for quick review.

---

## Getting Started

### Prerequisites
-   Python 3.9+
-   `git` for cloning the repository

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AryamanGupta001/debt-collection-call-analyzer.git
    cd all-convo-analysis
    ```

2.  **Create and activate a virtual environment:**
    *   **On macOS / Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   **On Windows:**
        ```bash
        python -m venv .venv
        .\.venv\Scripts\activate
        ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Usage

This project has two primary modes of operation: the interactive web app and the command-line batch processor.

#### 1. Interactive Analysis (Streamlit App)
Ideal for deep-diving into specific calls, training, or quality assurance reviews.

To run the app:
```bash
streamlit run app.py
```
Your web browser will open with the application interface, ready for you to upload call files.

#### 2. Batch Processing (Command-Line)
Ideal for analyzing large datasets and generating comprehensive reports.

To run the batch script on the sample data:
```bash
# Run in default (relaxed) compliance mode
python run_batch.py --input_dir data/

# Run in strict compliance mode
python run_batch.py --input_dir data/ --strict
```
Output files (`summary.csv`, `details.csv`, etc.) will be saved in the `results/` directory.

---

## Repository Structure

```
all-convo-analysis/
├── README.md                # This file
├── requirements.txt         # Project dependencies
├── app.py                   # The Streamlit web application
├── run_batch.py             # The CLI for batch processing
│
├── data/                    # Sample call transcript files (JSON/YAML)
├── patterns/                # Externalized detection rules (editable)
│   ├── profanity_patterns.txt
│   └── pii_patterns.txt
│
├── results/                 # Output directory for batch reports (CSV/XLSX)
├── src/                     # Core application source code
│   ├── io_json.py           # Robust data loading and normalization
│   ├── metrics.py           # Overtalk, silence, and talk-share calculations
│   ├── profanity.py         # Profanity detection logic
│   ├── pii_compliance.py    # PII/compliance violation logic
│   └── viz.py               # Visualization components (timeline, etc.)
│
└── ...```

---

## Strategic Positioning: Deterministic by Design

The decision to use a deterministic (regex-based) engine for this initial version was a deliberate strategic choice. It prioritizes **trust, auditability, and speed-to-value**. Compliance and legal teams can have 100% confidence in the system's findings because every flag is tied to an explicit, human-readable rule.

This approach not only delivers immediate value but also creates a high-quality, labeled dataset that will significantly accelerate and de-risk the future development of a more nuanced Machine Learning or LLM-based classifier in a subsequent phase.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.