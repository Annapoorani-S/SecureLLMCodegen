"""
AISAF Pipeline

AI Secure Architecture Framework

Complete Flow:

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
Promptfoo LLM Security Testing
        |
        v
Gemini Secure Code Generation
        |
        v
Parse Generated Files
        |
        v
Save Project
        |
        v
Bandit + Semgrep Scan
        |
        v
Gemini Fix Agent
        |
        v
Re-scan
        |
        v
Secure Output
"""


import os
import json
from datetime import datetime
from pathlib import Path


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
    SecurityScanner
)


from src.security_score import (
    calculate_security_score
)


from src.report_generator import (
    generate_report
)



OUTPUT_DIR = Path(
    "output"
)



REPORT_DIR = Path(
    "reports"
)



REPORT_DIR.mkdir(
    exist_ok=True
)



# ==========================================================
# Build AI Security Context
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
# Parse Gemini Generated Files
# ==========================================================


def parse_generated_files(response):


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
            "JSON parsing failed"
        )


        files = {

            "app.py":
                response

        }


    return files




# ==========================================================
# Save Generated Project
# ==========================================================


def save_files(files):


    saved=[]


    for filename,content in files.items():


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
        ) as f:


            f.write(
                content
            )


        saved.append(
            str(file_path)
        )


        print(
            f"✓ {file_path}"
        )


    return saved




# ==========================================================
# Fix Vulnerable Files
# ==========================================================


def remediate(findings):


    fixed_files=[]


    for issue in findings:


        file_path = Path(
            issue["file"]
        )


        if not file_path.exists():

            continue



        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:


            code=f.read()



        fixed_code = fix_vulnerable_code(
            code,
            issue
        )



        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:


            f.write(
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


    print(
        "\n" +
        "="*60
    )


    print(
        " AISAF - AI Secure Architecture Framework"
    )


    print(
        "="*60
    )



    # ------------------------------------------------------
    # STEP 1
    # ------------------------------------------------------


    print(
        "\n[1/4] Analysing security requirements..."
    )



    context = build_combined_context(
        requirement
    )



    print(
        "\nTechnology Stack Detected:"
    )


    for k,v in context["technology"].items():

        print(
            f"  {k:15}: {v}"
        )



    print(
        "\nOWASP Domains Detected:"
    )

    print(
        context["owasp_domains"]
    )


    print(
        "\nMITRE ATLAS Threats Detected:"
    )

    print(
        context["mitre_threats"]
    )




    # ------------------------------------------------------
    # Promptfoo
    # ------------------------------------------------------


    print(
        "\n[LLM SECURITY EVALUATION]"
    )


    promptfoo_report = run_promptfoo(
        requirement
    )



    print(
        "Promptfoo:",
        promptfoo_report.get(
            "status"
        )
    )




    # ------------------------------------------------------
    # STEP 2
    # ------------------------------------------------------


    print(
        "\n[2/4] Generating secure code via Gemini..."
    )


    response = generate_code(

        requirement,

        context

    )



    if not response:


        print(
            "[ERROR] Gemini returned no code"
        )


        return




    files = parse_generated_files(
        response
    )


    print(
        "\nFiles generated:",
        len(files)
    )



    saved_files = save_files(
        files
    )



    print(
        "\nCode generation complete!"
    )




    # ------------------------------------------------------
    # STEP 3
    # ------------------------------------------------------


    print(
        "\nAISAF SECURITY VALIDATION LOOP"
    )


    scanner = SecurityScanner()



    initial_report=None


    final_report=None



    for iteration in range(
        1,
        MAX_ITERATIONS+1
    ):


        print(
            f"\n===== SECURITY ITERATION {iteration} ====="
        )


        report = scanner.scan(
            OUTPUT_DIR
        )



        if iteration == 1:

            initial_report = report



        score = calculate_security_score(
            report
        )



        print(
            "\nCurrent Security Score:",
            score,
            "/100"
        )



        findings = report["findings"]



        if not findings:


            print(
                "✓ No vulnerabilities detected"
            )

            final_report=report

            break




        print(
            "\nVulnerabilities:"
        )


        for issue in findings:

            print(issue)



        print(
            "\nGemini Fix Agent running..."
        )


        remediate(
            findings
        )



        final_report=report





    # ------------------------------------------------------
    # STEP 4 REPORT
    # ------------------------------------------------------


    final_score = calculate_security_score(
        final_report
    )


    initial_score = calculate_security_score(
        initial_report
    )



    report_data={


        "framework":
            "AISAF",


        "timestamp":
            str(datetime.now()),


        "promptfoo":
            promptfoo_report.get(
                "status"
            ),


        "iterations":
            iteration,


        "initial_security_score":
            initial_score,


        "final_security_score":
            final_score,


        "status":
            "SECURE"
            if final_score == 100
            else
            "REQUIRES REVIEW"

    }



    generate_report(
        report_data
    )



    print(
        "\nAISAF SECURITY REPORT"
    )

    print(
        "="*60
    )


    print(
        json.dumps(
            report_data,
            indent=4
        )
    )



    return report_data





# ==========================================================
# TEST
# ==========================================================


if __name__=="__main__":


    requirement="""

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

    Deploy using Docker.

    """



    run_pipeline(
        requirement
    )