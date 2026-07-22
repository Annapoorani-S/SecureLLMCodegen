"""
fixer.py

AISAF Security Fixer

Reads scanner findings, builds a remediation prompt,
uses Gemini to repair vulnerable code,
and returns the fixed code.
"""

from pathlib import Path
from typing import Dict, List

from src.llm_client import generate_code


class SecurityFixer:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Read Vulnerable File
    # ---------------------------------------------------------

    def read_file(self, filepath: str) -> str:

        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(filepath)

        return path.read_text(encoding="utf-8")

    # ---------------------------------------------------------
    # Build Fix Prompt
    # ---------------------------------------------------------

    def build_fix_prompt(
        self,
        code: str,
        findings: List[Dict]
    ) -> str:

        prompt = """
You are an expert Secure Software Architect.

Your task is to repair ONLY the security vulnerabilities.

DO NOT remove existing functionality.

DO NOT change business logic.

Preserve formatting whenever possible.

Return ONLY the corrected source code.

====================================================
SECURITY FINDINGS
====================================================

"""

        for i, issue in enumerate(findings, start=1):

            prompt += f"""
Issue {i}

Tool      : {issue['tool']}
Severity  : {issue['severity']}
Rule      : {issue['rule']}
Line      : {issue['line']}

Description:
{issue['message']}

"""

        prompt += """

====================================================
SOURCE CODE
====================================================

"""

        prompt += code

        return prompt

    # ---------------------------------------------------------
    # Call Gemini
    # ---------------------------------------------------------

    def fix_code(
        self,
        code: str,
        findings: List[Dict]
    ) -> str:

        prompt = self.build_fix_prompt(
            code,
            findings
        )

        print("\n[Fixer] Sending prompt to Gemini...\n")

        fixed_code = generate_code(prompt)

        return fixed_code
    # ---------------------------------------------------------
    # Save Fixed Code
    # ---------------------------------------------------------

    def save_fixed_file(
        self,
        original_file: str,
        fixed_code: str
    ) -> str:

        original = Path(original_file)

        fixed_path = original.with_name(
            original.stem + "_fixed" + original.suffix
        )

        fixed_path.write_text(
            fixed_code,
            encoding="utf-8"
        )

        print(f"[Fixer] Saved fixed file: {fixed_path}")

        return str(fixed_path)

    # ---------------------------------------------------------
    # Fix Single File
    # ---------------------------------------------------------

    def fix_file(
        self,
        filepath: str,
        findings: List[Dict]
    ) -> Dict:

        print(f"\n[Fixer] Fixing {filepath}")

        code = self.read_file(filepath)

        fixed_code = self.fix_code(
            code,
            findings
        )

        fixed_path = self.save_fixed_file(
            filepath,
            fixed_code
        )

        return {

            "original": filepath,

            "fixed": fixed_path,

            "fixed_code": fixed_code

        }

    # ---------------------------------------------------------
    # Fix Multiple Files
    # ---------------------------------------------------------

    def fix_all(
        self,
        scanner_report: Dict
    ) -> List[Dict]:

        grouped = {}

        for issue in scanner_report["findings"]:

            grouped.setdefault(
                issue["file"],
                []
            ).append(issue)

        fixed_files = []

        for filepath, issues in grouped.items():

            try:

                fixed_files.append(

                    self.fix_file(
                        filepath,
                        issues
                    )

                )

            except Exception as e:

                print(
                    f"[Fixer] Failed to fix {filepath}: {e}"
                )

        return fixed_files


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    from src.scanner import SecurityScanner

    scanner = SecurityScanner()

    report = scanner.scan("../output")

    print("\n==============================")
    print("AISAF FIXER")
    print("==============================")

    if report["summary"]["total"] == 0:

        print("\nNo vulnerabilities found.")

    else:

        fixer = SecurityFixer()

        results = fixer.fix_all(report)

        print("\nFixed Files\n")

        for file in results:

            print("--------------------------------")

            print("Original :", file["original"])

            print("Fixed    :", file["fixed"])

        print("\nDone.")