"""
AISAF Report Generator

Creates security audit reports.
"""

import json
import os
from datetime import datetime



REPORT_DIR = "reports"



def generate_report(
        initial_report,
        final_report,
        initial_score,
        final_score,
        iterations
):


    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )


    improvement = (
        final_score - initial_score
    )



    report = {


        "framework":
        "AISAF",


        "timestamp":
        str(datetime.now()),


        "iterations":
        iterations,


        "initial_security_score":
        initial_score,


        "final_security_score":
        final_score,


        "security_improvement":
        f"{improvement}%",


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


        "status":
        "SECURE"
        if final_score == 100
        else
        "REQUIRES REVIEW"

    }



    path = os.path.join(
        REPORT_DIR,
        "security_report.json"
    )



    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            report,
            f,
            indent=4
        )



    print(
        "\nAISAF Report saved:",
        path
    )



    return report