"""
AISAF Security Scanner

Integrates:

1. Promptfoo
2. Bandit
3. Semgrep

Returns unified security findings.
"""


import json
import subprocess
from pathlib import Path



# ==========================================================
# Promptfoo Scanner
# ==========================================================


def run_promptfoo():

    print("\n[Scanner] Running Promptfoo LLM Security Tests...")

    try:

        result = subprocess.run(
            [
                "promptfoo",
                "eval",
                "--output",
                "reports/promptfoo_report.json"
            ],
            capture_output=True,
            text=True
        )


        if result.returncode != 0:

            return {

                "tool": "Promptfoo",

                "status": "FAILED",

                "message": result.stderr

            }


        return {

            "tool": "Promptfoo",

            "status": "PASSED",

            "message": "LLM security tests completed"

        }


    except Exception as e:

        return {

            "tool": "Promptfoo",

            "status": "ERROR",

            "message": str(e)

        }




# ==========================================================
# Bandit Scanner
# ==========================================================


def run_bandit(project_path):


    print("\n[Scanner] Running Bandit...")


    try:


        result = subprocess.run(

            [
                "python",
                "-m",
                "bandit",
                "-r",
                project_path,
                "-f",
                "json"
            ],

            capture_output=True,

            text=True

        )


        if result.stdout:


            data=json.loads(
                result.stdout
            )


            findings=[]


            for issue in data.get(
                "results",
                []
            ):


                findings.append({

                    "tool":"Bandit",

                    "severity":
                    issue.get(
                        "issue_severity"
                    ),

                    "file":
                    issue.get(
                        "filename"
                    ),

                    "line":
                    issue.get(
                        "line_number"
                    ),

                    "rule":
                    issue.get(
                        "test_id"
                    ),

                    "message":
                    issue.get(
                        "issue_text"
                    )

                })


            return findings



        return []



    except Exception as e:


        print(
            "Bandit Error:",
            e
        )

        return []




# ==========================================================
# Semgrep Scanner
# ==========================================================


def run_semgrep(project_path):


    print(
        "\n[Scanner] Running Semgrep..."
    )


    try:


        result=subprocess.run(

            [
                "python",
                "-m",
                "semgrep",
                "--config=auto",
                project_path,
                "--json"
            ],

            capture_output=True,

            text=True

        )



        if result.stdout:


            data=json.loads(
                result.stdout
            )


            findings=[]


            for issue in data.get(
                "results",
                []
            ):


                findings.append({

                    "tool":"Semgrep",

                    "severity":
                    issue.get(
                        "extra",
                        {}
                    ).get(
                        "severity",
                        "INFO"
                    ),


                    "file":
                    issue.get(
                        "path"
                    ),


                    "line":
                    issue.get(
                        "start",
                        {}
                    ).get(
                        "line"
                    ),


                    "rule":
                    issue.get(
                        "check_id"
                    ),


                    "message":
                    issue.get(
                        "extra",
                        {}
                    ).get(
                        "message"
                    )

                })


            return findings



        return []



    except Exception as e:


        print(
            "Semgrep Error:",
            e
        )

        return []




# ==========================================================
# Unified AISAF Scanner
# ==========================================================


def scan_project(project_path):


    findings=[]


    # Promptfoo

    prompt_result = run_promptfoo()


    if prompt_result["status"] != "PASSED":

        findings.append(
            prompt_result
        )



    # Code scanners

    findings.extend(
        run_bandit(
            project_path
        )
    )


    findings.extend(
        run_semgrep(
            project_path
        )
    )



    return {


        "total":
        len(findings),


        "issues":
        findings

    }



# ==========================================================
# Test
# ==========================================================


if __name__=="__main__":


    report=scan_project(
        "../output"
    )


    print(
        json.dumps(
            report,
            indent=4
        )
    )