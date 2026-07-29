"""
AISAF Pipeline

AI Secure Architecture Framework

Complete Secure Code Generation Pipeline

Flow:

Requirement
        |
        v
Technology Classification
        |
        v
OWASP Security Context
        |
        v
MITRE ATLAS Threat Context
        |
        v
Promptfoo LLM Evaluation
        |
        v
Gemini Secure Code Generation
        |
        v
Project Parsing
        |
        v
Security Scanning
        |
        v
Automatic Remediation
        |
        v
Security Report
"""


import os
import json
import time

from pathlib import Path
from datetime import datetime


# ==========================================================
# Imports
# ==========================================================


from src.config import MAX_ITERATIONS


from src.tech_classifier import (
    classify_technology
)


from src.owasp_context import (
    detect_security_domains,
    build_security_context
)


from src.mitre_context import (
    detect_ai_threats,
    build_mitre_context
)


from src.prompt_security import (
    run_promptfoo
)


from src.llm_client import (
    generate_code,
    fix_vulnerable_code
)


from src.scanner import (
    scan_project
)


from src.security_score import (
    calculate_security_score,
    security_status,
    security_metrics
)


from src.report_generator import (
    generate_report
)



# ==========================================================
# Directories
# ==========================================================


OUTPUT_DIR = Path(
    "output"
)


REPORT_DIR = Path(
    "reports"
)


OUTPUT_DIR.mkdir(
    exist_ok=True
)


REPORT_DIR.mkdir(
    exist_ok=True
)



# ==========================================================
# Build AISAF Security Context
# ==========================================================


def build_combined_context(requirement):


    technology = classify_technology(
        requirement
    )


    owasp_domains = detect_security_domains(
        requirement
    )


    mitre_threats = detect_ai_threats(
        requirement
    )


    security_context = build_security_context(
        requirement
    )


    mitre_context = build_mitre_context(
        requirement
    )


    return {


        "technology":
            technology,


        "owasp_domains":
            owasp_domains,


        "mitre_threats":
            mitre_threats,


        "security_context":
            security_context,


        "mitre_context":
            mitre_context

    }
# ==========================================================
# Gemini Code Generation
# ==========================================================


def generate_secure_project(
        requirement,
        context
):

    """
    Generate secure project using Gemini.
    """

    print(
        "\n[Gemini] Generating secure project..."
    )


    retries = 3


    for attempt in range(
        retries
    ):

        try:

            response = generate_code(

                requirement,

                context

            )


            if response:

                return response



        except Exception as e:


            error = str(e)


            print(
                "\n[Gemini Error]",
                error
            )


            # Gemini quota / temporary errors

            if (
                "429" in error
                or
                "503" in error
            ):

                wait_time = (
                    30 * (attempt + 1)
                )


                print(
                    f"Retrying after {wait_time}s..."
                )


                time.sleep(
                    wait_time
                )


            else:

                break



    print(
        "\nGemini failed after retries."
    )


    return None





# ==========================================================
# Parse Generated Files
# ==========================================================


def parse_generated_files(
        response
):


    files = {}


    try:


        data = json.loads(
            response
        )


        files = data.get(
            "files",
            {}
        )



    except Exception:


        print(
            "JSON parsing failed."
        )


        files = {


            "app.py":
                response

        }



    return files





# ==========================================================
# Save Generated Project
# ==========================================================


def save_files(
        files
):


    saved_files = []



    for filename, content in files.items():


        file_path = (
            OUTPUT_DIR /
            filename
        )



        file_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )



        with open(

            file_path,

            "w",

            encoding="utf-8"

        ) as file:


            file.write(
                content
            )



        saved_files.append(
            str(file_path)
        )



        print(
            f"✓ Saved {file_path}"
        )



    return saved_files





# ==========================================================
# Automatic Remediation
# ==========================================================


def remediate(
        findings
):


    fixed_files = []



    for issue in findings:


        file_name = issue.get(
            "file"
        )


        if not file_name:

            continue



        file_path = Path(
            file_name
        )



        if not file_path.exists():


            continue




        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as file:


            code = file.read()




        print(

            "\n[Gemini Fix Agent] Analysing vulnerability..."

        )



        fixed_code = fix_vulnerable_code(

            code,

            issue

        )



        if fixed_code:


            with open(

                file_path,

                "w",

                encoding="utf-8"

            ) as file:


                file.write(
                    fixed_code
                )



            fixed_files.append(
                str(file_path)
            )



            print(
                f"✓ Fixed: {file_path}"
            )



    return fixed_files
# ==========================================================
# MAIN PIPELINE
# ==========================================================


def run_pipeline(requirement):


    print("\n" + "=" * 60)

    print(
        " AISAF - AI Secure Architecture Framework"
    )

    print("=" * 60)



    # ======================================================
    # STEP 1
    # Requirement Analysis
    # ======================================================


    print(
        "\n[1/4] Analysing security requirements..."
    )


    context = build_combined_context(
        requirement
    )



    print(
        "\nTechnology Stack Detected:"
    )


    for key, value in context["technology"].items():

        print(
            f"  {key:<15}: {value}"
        )



    print(
        "\nOWASP Domains Detected:"
    )

    print(
        ", ".join(
            context["owasp_domains"]
        )
    )



    print(
        "\nMITRE ATLAS Threats Detected:"
    )

    print(
        ", ".join(
            context["mitre_threats"]
        )
    )



    # ======================================================
    # Promptfoo Security Evaluation
    # ======================================================


    print(
        "\n[LLM SECURITY EVALUATION]"
    )


    try:


        promptfoo_report = run_promptfoo(
            requirement
        )


        print(
            "Promptfoo Status:",
            promptfoo_report.get(
                "status"
            )
        )


    except Exception as e:


        print(
            "Promptfoo Error:",
            e
        )


        promptfoo_report = {


            "status":
            "FAILED",

            "error":
            str(e)

        }





    # ======================================================
    # STEP 2
    # Secure Code Generation
    # ======================================================


    print(
        "\n[2/4] Generating secure code via Gemini..."
    )



    response = generate_secure_project(

        requirement,

        context

    )



    if not response:


        print(
            "\n[ERROR] Gemini did not return code."
        )


        return None




    files = parse_generated_files(
        response
    )



    print(
        "\nFiles generated:",
        len(files)
    )



    save_files(
        files
    )



    print(
        "\nCode generation complete!"
    )





    # ======================================================
    # STEP 3
    # Security Validation Loop
    # ======================================================


    print(

        "\n" +
        "=" * 60

    )


    print(
        " AISAF SECURITY VALIDATION LOOP"
    )


    print(
        "=" * 60
    )



    initial_report = None

    final_report = None


    initial_score = 0

    final_score = 0



    for iteration in range(

        1,

        MAX_ITERATIONS + 1

    ):


        print(

            f"\n===== SECURITY ITERATION {iteration} ====="

        )



        report = scan_project(

            str(
                OUTPUT_DIR
            )

        )



        if iteration == 1:


            initial_report = report



            initial_score = calculate_security_score(

                report

            )



        score = calculate_security_score(

            report

        )



        metrics = security_metrics(

            report

        )



        print(

            "\nCurrent Security Score:",
            score,
            "/100"

        )



        print(

            "Security Status:",
            metrics["status"]

        )



        findings = report.get(

            "issues",

            []

        )



        if not findings:


            print(

                "✓ No vulnerabilities detected"

            )


            final_report = report

            final_score = score

            break




        print(

            "\nVulnerabilities Detected:"

        )



        for issue in findings:


            print(issue)




        print(

            "\nGemini Fix Agent running..."

        )



        remediate(

            findings

        )



        final_report = report

        final_score = score
# ==========================================================
# STEP 4
# AISAF Report Generation
# ==========================================================


    if final_report is None:

        final_report = scan_project(
            str(OUTPUT_DIR)
        )

        final_score = calculate_security_score(
            final_report
        )



    print(

        "\nGenerating AISAF Security Report..."

    )



    report = generate_report(

        initial_report,

        final_report,

        initial_score,

        final_score,

        iteration,

        technology=context["technology"],

        owasp_domains=context["owasp_domains"],

        mitre_threats=context["mitre_threats"]

    )



    print(

        "\n" +
        "=" * 60

    )


    print(

        " AISAF SECURITY REPORT"

    )


    print(

        "=" * 60

    )



    print(

        json.dumps(

            report,

            indent=4

        )

    )



    return report





# ==========================================================
# TEST EXECUTION
# ==========================================================


if __name__ == "__main__":


    requirement = """

    Build a secure banking REST API.

    Technology:
    Java Spring Boot

    Database:
    PostgreSQL

    Features:

    - JWT Authentication
    - User management
    - Transactions
    - Role based authorization

    Deployment:
    Docker

    """


    run_pipeline(

        requirement

    )
