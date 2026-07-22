"""
bandit_scanner.py

AISAF Bandit Scanner
"""

import json
import subprocess


def run_bandit(project_path):
    """
    Run Bandit and return AISAF findings.
    """

    print("\n[Scanner] Running Bandit...")

    findings = []

    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "bandit",
                "-r",
                project_path,
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():

            data = json.loads(result.stdout)

            for issue in data.get("results", []):

                findings.append(
                    {
                        "tool": "Bandit",
                        "severity": issue.get("issue_severity", "LOW"),
                        "confidence": issue.get("issue_confidence", "MEDIUM"),
                        "file": issue.get("filename"),
                        "line": issue.get("line_number"),
                        "rule": issue.get("test_id"),
                        "message": issue.get("issue_text"),
                    }
                )

    except Exception as e:

        print("[Bandit Error]", e)

    return findings


if __name__ == "__main__":

    report = run_bandit("../output")

    print(report)