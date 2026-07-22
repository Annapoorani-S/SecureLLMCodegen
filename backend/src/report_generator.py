"""
report_generator.py

AISAF Report Generator

Generates:

1. JSON Report
2. Markdown Report
3. HTML Report
"""

import json
import os
from datetime import datetime


REPORT_DIR = "reports"


# ==========================================================
# Utilities
# ==========================================================

def ensure_report_directory():
    """
    Create reports directory if it doesn't exist.
    """

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )


def calculate_improvement(
    initial_score,
    final_score
):
    """
    Calculate percentage improvement.
    """

    return final_score - initial_score


def build_report(
    initial_report,
    final_report,
    initial_score,
    final_score,
    iterations,
    technology=None,
    owasp_domains=None,
    mitre_threats=None
):
    """
    Build AISAF report dictionary.
    """

    improvement = calculate_improvement(
        initial_score,
        final_score
    )

    report = {

        "framework": "AISAF",

        "version": "1.0",

        "timestamp": str(
            datetime.now()
        ),

        "iterations": iterations,

        "initial_security_score":
            initial_score,

        "final_security_score":
            final_score,

        "security_improvement":
            f"{improvement}%",

        "technology_stack":
            technology or {},

        "owasp_domains":
            owasp_domains or [],

        "mitre_atlas":
            mitre_threats or [],

        "summary": final_report.get(
            "summary",
            {}
        ),

        "initial_vulnerabilities":
            initial_report.get(
                "issues",
                []
            ),

        "final_vulnerabilities":
            final_report.get(
                "issues",
                []
            ),

        "status": (
            "SECURE"
            if final_score >= 95
            else "REQUIRES REVIEW"
        )

    }

    return report


# ==========================================================
# JSON Report
# ==========================================================

def save_json_report(report):
    """
    Save JSON report.
    """

    path = os.path.join(
        REPORT_DIR,
        "security_report.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"\n✓ JSON Report Saved : {path}"
    )

    return path


# ==========================================================
# Markdown Report
# ==========================================================

def build_markdown(report):
    """
    Convert report into Markdown.
    """

    md = []

    md.append("# AISAF Security Report\n")

    md.append(
        f"**Generated:** {report['timestamp']}\n"
    )

    md.append(
        f"**Framework:** {report['framework']}\n"
    )

    md.append(
        f"**Version:** {report['version']}\n"
    )

    md.append("---\n")

    md.append("## Security Score\n")

    md.append(
        f"- Initial Score : {report['initial_security_score']}\n"
    )

    md.append(
        f"- Final Score : {report['final_security_score']}\n"
    )

    md.append(
        f"- Improvement : {report['security_improvement']}\n"
    )

    md.append(
        f"- Status : {report['status']}\n"
    )

    md.append("\n---\n")

    md.append("## Technology Stack\n")

    for key, value in report[
        "technology_stack"
    ].items():

        md.append(
            f"- **{key}** : {value}\n"
        )

    md.append("\n---\n")

    return "".join(md)
# ==========================================================
# Save Markdown Report
# ==========================================================

def save_markdown_report(report):
    """
    Save Markdown report.
    """

    path = os.path.join(
        REPORT_DIR,
        "security_report.md"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            build_markdown(report)
        )

    print(
        f"✓ Markdown Report Saved : {path}"
    )

    return path


# ==========================================================
# HTML Report
# ==========================================================

def build_html(report):
    """
    Build HTML security report.
    """

    html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>AISAF Security Report</title>

<style>

body{{
font-family:Arial;
margin:40px;
background:#f5f5f5;
}}

h1{{
color:#0b5394;
}}

table{{
border-collapse:collapse;
width:100%;
background:white;
}}

th,td{{
border:1px solid #ccc;
padding:10px;
}}

th{{
background:#eeeeee;
}}

.success{{
color:green;
font-weight:bold;
}}

.warning{{
color:red;
font-weight:bold;
}}

</style>

</head>

<body>

<h1>AISAF Security Report</h1>

<p><b>Framework:</b> {report['framework']}</p>
<p><b>Version:</b> {report['version']}</p>
<p><b>Generated:</b> {report['timestamp']}</p>

<h2>Security Score</h2>

<table>

<tr>
<th>Metric</th>
<th>Value</th>
</tr>

<tr>
<td>Initial Score</td>
<td>{report['initial_security_score']}</td>
</tr>

<tr>
<td>Final Score</td>
<td>{report['final_security_score']}</td>
</tr>

<tr>
<td>Improvement</td>
<td>{report['security_improvement']}</td>
</tr>

<tr>
<td>Status</td>
<td>{report['status']}</td>
</tr>

</table>

<h2>Technology Stack</h2>

<table>

<tr>

<th>Component</th>

<th>Detected</th>

</tr>

"""

    for key, value in report["technology_stack"].items():

        html += f"""
<tr>
<td>{key}</td>
<td>{value}</td>
</tr>
"""

    html += """

</table>

<h2>Security Summary</h2>

<table>

<tr>
<th>Total Findings</th>
<th>High</th>
<th>Medium</th>
<th>Low</th>
<th>Info</th>
</tr>

<tr>

<td>{total}</td>
<td>{high}</td>
<td>{medium}</td>
<td>{low}</td>
<td>{info}</td>

</tr>

</table>

""".format(
        total=report["summary"].get("total", 0),
        high=report["summary"].get("HIGH", 0),
        medium=report["summary"].get("MEDIUM", 0),
        low=report["summary"].get("LOW", 0),
        info=report["summary"].get("INFO", 0),
    )

    html += """

<h2>Final Vulnerabilities</h2>

<table>

<tr>

<th>Tool</th>

<th>Severity</th>

<th>Rule</th>

<th>Message</th>

</tr>

"""

    for issue in report["final_vulnerabilities"]:

        html += f"""
<tr>

<td>{issue.get('tool','')}</td>

<td>{issue.get('severity','')}</td>

<td>{issue.get('rule','')}</td>

<td>{issue.get('message','')}</td>

</tr>
"""

    html += """

</table>

</body>

</html>

"""

    return html


# ==========================================================
# Save HTML
# ==========================================================

def save_html_report(report):

    path = os.path.join(
        REPORT_DIR,
        "security_report.html"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            build_html(report)
        )

    print(
        f"✓ HTML Report Saved : {path}"
    )

    return path


# ==========================================================
# Main Report Generator
# ==========================================================

def generate_report(
    initial_report,
    final_report,
    initial_score,
    final_score,
    iterations,
    technology=None,
    owasp_domains=None,
    mitre_threats=None
):
    """
    Generate every AISAF report.
    """

    ensure_report_directory()

    report = build_report(
        initial_report,
        final_report,
        initial_score,
        final_score,
        iterations,
        technology,
        owasp_domains,
        mitre_threats
    )

    save_json_report(report)

    save_markdown_report(report)

    save_html_report(report)

    print("\n✓ AISAF Reports Generated Successfully")

    return report


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = {

        "summary": {

            "total": 2,

            "HIGH": 1,

            "MEDIUM": 1,

            "LOW": 0,

            "INFO": 0

        },

        "issues": [

            {

                "tool": "Bandit",

                "severity": "HIGH",

                "rule": "B201",

                "message": "Debug mode enabled"

            }

        ]

    }

    generate_report(

        sample,

        sample,

        70,

        95,

        2,

        technology={

            "language": "Python",

            "framework": "Flask",

            "database": "PostgreSQL"

        },

        owasp_domains=[

            "Authentication",

            "SQL Injection"

        ],

        mitre_threats=[

            "Prompt Injection"

        ]

    )