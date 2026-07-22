"""
scanner.py

AISAF Unified Security Scanner

Combines:
1. Promptfoo
2. Bandit
3. Semgrep

Returns one unified security report.
"""

from src.promptfoo_scanner import scan_promptfoo
from src.bandit_scanner import run_bandit
from src.semgrep_scanner import run_semgrep


# ==========================================================
# Summary Generator
# ==========================================================

def build_summary(findings):
    """
    Count vulnerabilities by severity.
    """

    summary = {
        "total": len(findings),
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "INFO": 0,
    }

    for issue in findings:

        severity = str(
            issue.get("severity", "INFO")
        ).upper()

        if severity not in summary:
            severity = "INFO"

        summary[severity] += 1

    return summary


# ==========================================================
# Unified Scanner
# ==========================================================

def scan_project(project_path):
    """
    Run every scanner and merge findings.
    """

    print("\n" + "=" * 60)
    print(" AISAF Unified Security Scanner")
    print("=" * 60)

    findings = []

    # --------------------------------------------------
    # Promptfoo
    # --------------------------------------------------

    try:

        promptfoo_findings = scan_promptfoo()

        findings.extend(promptfoo_findings)

    except Exception as e:

        print("[Promptfoo Error]", e)

    # --------------------------------------------------
    # Bandit
    # --------------------------------------------------

    try:

        bandit_findings = run_bandit(project_path)

        findings.extend(bandit_findings)

    except Exception as e:

        print("[Bandit Error]", e)

    # --------------------------------------------------
    # Semgrep
    # --------------------------------------------------

    try:

        semgrep_findings = run_semgrep(project_path)

        findings.extend(semgrep_findings)

    except Exception as e:

        print("[Semgrep Error]", e)

    summary = build_summary(findings)

    print("\nSecurity Summary")
    print("-" * 40)

    print(f"Total Findings : {summary['total']}")
    print(f"HIGH           : {summary['HIGH']}")
    print(f"MEDIUM         : {summary['MEDIUM']}")
    print(f"LOW            : {summary['LOW']}")
    print(f"INFO           : {summary['INFO']}")

    return {
        "total": summary["total"],
        "issues": findings,
        "summary": summary,
    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    report = scan_project("output")

    print("\n")

    for issue in report["issues"]:

        print(issue)