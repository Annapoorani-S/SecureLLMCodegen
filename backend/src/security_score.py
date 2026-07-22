"""
security_score.py

AISAF Security Score Engine

Calculates an overall security score
from Promptfoo, Bandit and Semgrep findings.
"""


# ==========================================================
# Severity Weights
# ==========================================================

SEVERITY_WEIGHTS = {
    "CRITICAL": 30,
    "HIGH": 20,
    "MEDIUM": 10,
    "LOW": 5,
    "INFO": 1,
}


# ==========================================================
# Calculate Score
# ==========================================================

def calculate_security_score(report):
    """
    Calculate overall security score.

    Input:
        report = {
            "issues": [...]
        }

    Returns:
        Integer score (0-100)
    """

    score = 100

    issues = report.get("issues", [])

    for issue in issues:

        severity = str(
            issue.get("severity", "LOW")
        ).upper()

        deduction = SEVERITY_WEIGHTS.get(
            severity,
            5
        )

        score -= deduction

    if score < 0:
        score = 0

    return score


# ==========================================================
# Risk Level
# ==========================================================

def security_status(score):

    if score >= 95:
        return "SECURE"

    elif score >= 80:
        return "LOW RISK"

    elif score >= 60:
        return "MODERATE RISK"

    elif score >= 40:
        return "HIGH RISK"

    else:
        return "CRITICAL"


# ==========================================================
# Detailed Metrics
# ==========================================================

def security_metrics(report):
    """
    Build detailed metrics for reports.
    """

    summary = report.get("summary", {})

    score = calculate_security_score(report)

    return {

        "score": score,

        "status": security_status(score),

        "total_findings": summary.get(
            "total",
            0
        ),

        "high": summary.get(
            "HIGH",
            0
        ),

        "medium": summary.get(
            "MEDIUM",
            0
        ),

        "low": summary.get(
            "LOW",
            0
        ),

        "info": summary.get(
            "INFO",
            0
        )

    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = {

        "summary": {

            "total": 5,

            "HIGH": 1,

            "MEDIUM": 2,

            "LOW": 1,

            "INFO": 1

        },

        "issues": [

            {"severity": "HIGH"},

            {"severity": "MEDIUM"},

            {"severity": "MEDIUM"},

            {"severity": "LOW"},

            {"severity": "INFO"}

        ]

    }

    metrics = security_metrics(sample)

    print(metrics)