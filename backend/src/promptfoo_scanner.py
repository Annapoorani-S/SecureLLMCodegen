"""
promptfoo_scanner.py

AISAF Promptfoo Integration

Runs Promptfoo evaluation and converts its
results into AISAF vulnerability findings.
"""

import json
import subprocess
from pathlib import Path


PROMPTFOO_REPORT = Path("reports/promptfoo_results.json")


def run_promptfoo():
    """
    Execute Promptfoo evaluation.
    """

    print("\n[Scanner] Running Promptfoo...")

    try:

        subprocess.run(
            ["npx", "promptfoo", "eval"],
            check=True
        )

        return True

    except Exception as e:

        print("[Promptfoo Error]", e)
        return False


def load_promptfoo_results():
    """
    Load Promptfoo JSON report.
    """

    if not PROMPTFOO_REPORT.exists():
        return None

    with open(PROMPTFOO_REPORT, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_to_findings(report):
    """
    Convert Promptfoo output into AISAF findings.
    """

    findings = []

    if not report:
        return findings

    results = report.get("results", [])

    for result in results:

        passed = result.get("success", True)

        if passed:
            continue

        findings.append({

            "tool": "Promptfoo",
            "severity": "HIGH",
            "confidence": "HIGH",
            "file": "LLM Prompt",
            "line": "-",
            "rule": result.get("description", "Prompt Security"),
            "message": "Prompt security evaluation failed."

        })

    return findings


def scan_promptfoo():
    """
    Run Promptfoo and return AISAF findings.
    """

    success = run_promptfoo()

    if not success:
        return []

    report = load_promptfoo_results()

    return convert_to_findings(report)