# run_batch.py
import argparse
from pathlib import Path
import csv
import json
from src.io_json import load_file
from src.profanity import detect_profanity
from src.pii_compliance import detect_compliance_violation
from src.metrics import overtalk_percentage, silence_percentage
from src.metrics import talk_share

def process_file(path: Path, strict=False):
    try:
        utt = load_file(path)
    except Exception as e:
        return {"call_id": path.stem, "error": str(e)}

    ot = overtalk_percentage(utt)
    si = silence_percentage(utt)
    tt = talk_share(utt)

    prof = detect_profanity(utt)
    comp = detect_compliance_violation(utt, strict=strict)

    return {
        "call_id": Path(path).stem,
        "agent_prof": "Yes" if prof.get("agent_has") else "No",
        "borrower_prof": "Yes" if prof.get("borrower_has") else "No",
        "compliance_violation": "Yes" if comp.get("violation") else "No",
        "overtalk_pct": f"{ot:.2f}%",
        "silence_pct": f"{si:.2f}%",
        "total_time": f"{tt['total']:.1f}s",
        "agent_share": f"{tt['agent_pct']:.1f}%",
        "borrower_share": f"{tt['borrower_pct']:.1f}%",
        "prof_details": prof,
        "comp_details": comp,
    }

def main():
    ap = argparse.ArgumentParser(description="Batch process call transcripts")
    ap.add_argument("--input_dir", required=True, help="Directory containing JSON/YAML files")
    ap.add_argument("--strict", action="store_true", help="Enable strict compliance verification")
    args = ap.parse_args()

    input_path = Path(args.input_dir)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    files = list(input_path.glob("**/*.json")) + list(input_path.glob("**/*.yaml")) + list(input_path.glob("**/*.yml"))

    summary_rows, detail_rows = [], []
    for f in files:
        res = process_file(f, strict=args.strict)
        if "error" in res:
            print(f"Skipping {f.name}: {res['error']}")
            continue

        summary_rows.append({
            "File (Call ID)": res["call_id"],
            "Agent Profanity": res["agent_prof"],
            "Borrower Profanity": res["borrower_prof"],
            "Compliance Violation": res["compliance_violation"],
            "Overtalk %": res["overtalk_pct"],
            "Silence %": res["silence_pct"],
            "Total Time": res["total_time"],
            "Agent Talk %": res["agent_share"],
            "Borrower Talk %": res["borrower_share"]
        })


        # Profanity evidence
        for hit in res["prof_details"].get("hits", []):
            detail_rows.append({
                "File (Call ID)": res["call_id"],
                "Type": "Profanity",
                "Speaker": hit.get("speaker", ""),
                "Text": hit.get("text", ""),
                "Matches": ", ".join(hit.get("matches", []))
            })

        # Compliance evidence
        ev = res["comp_details"].get("evidence", {})
        if isinstance(ev, dict) and ev.get("reason"):
            detail_rows.append({
                "File (Call ID)": res["call_id"],
                "Type": "Compliance",
                "Speaker": "agent",
                "Text": ev.get("reason", ""),
                "Matches": json.dumps(ev.get("examples", []))
            })

    # Determine output filenames based on strict mode
    if args.strict:
        summary_file = results_dir / "summary_strict.csv"
        details_file = results_dir / "details_strict.csv"
    else:
        summary_file = results_dir / "summary.csv"
        details_file = results_dir / "details.csv"

    # Save summary CSV
    keys = [
        "File (Call ID)",
        "Agent Profanity",
        "Borrower Profanity",
        "Compliance Violation",
        "Overtalk %", "Silence %",
        "Total Time", "Agent Talk %", "Borrower Talk %"
    ]
    with open(summary_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, keys)
        writer.writeheader()
        writer.writerows(summary_rows)

    # Save details CSV (use appropriate keys for details_rows)
    detail_keys = detail_rows[0].keys() if detail_rows else []
    with open(details_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, detail_keys)
        writer.writeheader()
        writer.writerows(detail_rows)

    print(f"✅ Summary saved to {summary_file}")
    if detail_rows:
        print(f"✅ Details saved to {details_file}")


if __name__ == "__main__":
    main()
