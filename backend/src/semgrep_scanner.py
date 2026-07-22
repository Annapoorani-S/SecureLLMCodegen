"""
semgrep_scanner.py

AISAF Semgrep Scanner
"""

import json
import subprocess


def run_semgrep(project_path):
    """
    Run Semgrep and return AISAF findings.
    """

    print("\n[Scanner] Running Semgrep...")

    findings = []

    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "semgrep",
                "--config=auto",
                project_path,
                "--json",
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():

            data = json.loads(result.stdout)

            for issue in data.get("results", []):

                findings.append(
                    {
                        "tool": "Semgrep",
                        "severity": issue.get("extra", {}).get(
                            "severity",
                            "INFO",
                        ),
                        "confidence": issue.get("extra", {}).get(
                            "confidence",
                            "MEDIUM",
                        ),
                        "file": issue.get("path"),
                        "line": issue.get("start", {}).get("line"),
                        "rule": issue.get("check_id"),
                        "message": issue.get("extra", {}).get(
                            "message",
                            ""
                        ),
                    }
                )

    except Exception as e:

        print("[Semgrep Error]", e)

    return findings


if __name__ == "__main__":

    report = run_semgrep("../output")

    print(report)