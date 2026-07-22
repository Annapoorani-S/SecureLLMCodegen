"""
AISAF Prompt Security Evaluator

Integrates Promptfoo for LLM security testing.

Checks:
- Prompt Injection resistance
- Secure coding compliance
- Secret leakage resistance
"""

import subprocess
import json
from pathlib import Path


REPORT_FILE = "reports/promptfoo_report.json"


def run_promptfoo(requirement: str):

    print("\n[Promptfoo] Running LLM Security Evaluation...")


    try:

        result = subprocess.run(

            [
                "promptfoo",
                "eval",
                "-o",
                REPORT_FILE
            ],

            capture_output=True,

            text=True

        )


        if result.returncode != 0:

            print(
                "[Promptfoo Error]"
            )

            print(
                result.stderr
            )


            return {

                "status": "FAILED",

                "error": result.stderr

            }


        report_path = Path(
            REPORT_FILE
        )


        if report_path.exists():


            with open(
                report_path,
                "r"
            ) as file:


                data = json.load(file)


            return {

                "status": "COMPLETED",

                "report": data

            }


        return {

            "status": "COMPLETED"

        }



    except Exception as e:


        return {

            "status":"FAILED",

            "error":str(e)

        }