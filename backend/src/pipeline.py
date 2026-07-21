"""
pipeline.py

AISAF Unified Security Pipeline.

Orchestrates the full flow:

    User Requirement
          |
          v
    Security Domain Detection (OWASP)
          |
          v
    AI Threat Detection (MITRE ATLAS)
          |
          v
    Context Merging
          |
          v
    Groq Secure Code Generation
          |
          v
    File Parsing & Output Saving

Public API:
    run_pipeline(requirement, output_dir) -> dict
"""

import os
import re
from pathlib import Path

from src.owasp_context import detect_security_domains, build_security_context
from src.mitre_context import detect_ai_threats, build_mitre_context
from src.llm_client import generate_code


# ------------------------------------------------------------------
# Context Builder
# ------------------------------------------------------------------

def build_combined_context(requirement: str) -> tuple[str, list[str], list[str]]:
    """
    Build a combined OWASP + MITRE ATLAS security context.

    Args:
        requirement: User's software requirement.

    Returns:
        Tuple of (combined_context_str, owasp_domains, mitre_threats)
    """

    # ── OWASP ─────────────────────────────────────────────────────
    owasp_domains = detect_security_domains(requirement)
    owasp_context = build_security_context(requirement)

    # ── MITRE ATLAS ────────────────────────────────────────────────
    mitre_threats = detect_ai_threats(requirement)
    mitre_context = build_mitre_context(requirement)

    # ── Merge ──────────────────────────────────────────────────────
    parts = [owasp_context]

    if mitre_context:
        parts.append(mitre_context)

    combined = "\n\n".join(parts)

    return combined, owasp_domains, mitre_threats


# ------------------------------------------------------------------
# File Parser
# ------------------------------------------------------------------

def parse_generated_files(raw_output: str) -> dict[str, str]:
    """
    Parse the LLM response into individual files.

    The LLM is instructed to return files in this format:

        === FILE: path/to/file.py ===
        <file content>

        === FILE: another/file.js ===
        <file content>

    Args:
        raw_output: Raw text returned by the LLM.

    Returns:
        Dict mapping file path → file content.
    """

    files = {}

    # Split on the file header markers
    pattern = r"===\s*FILE:\s*(.+?)\s*==="
    parts = re.split(pattern, raw_output)

    # parts = [preamble, filename1, content1, filename2, content2, ...]
    it = iter(parts[1:])  # skip the preamble

    for filename, content in zip(it, it):
        filename = filename.strip()
        content = content.strip()

        # Strip any leading/trailing markdown fences from content
        content = re.sub(r"^```[\w+-]*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        content = content.strip()

        if filename and content:
            files[filename] = content

    return files


# ------------------------------------------------------------------
# Output Saver
# ------------------------------------------------------------------

def save_files(files: dict[str, str], output_dir: str) -> list[str]:
    """
    Save generated files to the output directory.

    Args:
        files: Dict of filename → content.
        output_dir: Root directory to save files into.

    Returns:
        List of absolute paths that were saved.
    """

    saved = []
    output_path = Path(output_dir)

    for filename, content in files.items():
        file_path = output_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        saved.append(str(file_path))

    return saved


# ------------------------------------------------------------------
# Main Pipeline Entry Point
# ------------------------------------------------------------------

def run_pipeline(
    requirement: str,
    output_dir: str = "output"
) -> dict:
    """
    Run the full AISAF secure code generation pipeline.

    Steps:
        1. Detect OWASP security domains.
        2. Detect MITRE ATLAS AI threats.
        3. Build combined security context.
        4. Generate secure code via Groq.
        5. Parse output into individual files.
        6. Save files to output_dir.

    Args:
        requirement: User's natural language software requirement.
        output_dir:  Directory where generated files will be saved.
                     Defaults to 'output/'.

    Returns:
        Dict with keys:
            owasp_domains   - list of detected OWASP domains
            mitre_threats   - list of detected MITRE ATLAS threats
            security_context - combined security context string
            raw_output      - raw Groq response
            files           - dict of filename → content
            saved_paths     - list of saved file paths
    """

    print("\n" + "=" * 60)
    print("  AISAF – AI Secure Architecture Framework")
    print("=" * 60)

    # ── Step 1 & 2: Detect threats ────────────────────────────────
    print("\n[1/4] Analysing security requirements...")

    combined_context, owasp_domains, mitre_threats = build_combined_context(requirement)

    print(f"\n  OWASP Domains Detected   : {', '.join(owasp_domains) if owasp_domains else 'None'}")
    print(f"  MITRE ATLAS Threats Detected: {', '.join(mitre_threats) if mitre_threats else 'None'}")

    # ── Step 3: Generate code ─────────────────────────────────────
    print("\n[2/4] Generating secure code via Groq...")

    raw_output = generate_code(requirement, combined_context)

    # ── Step 4: Parse files ───────────────────────────────────────
    print("\n[3/4] Parsing generated files...")

    files = parse_generated_files(raw_output)

    if not files:
        # Fallback: treat the entire output as a single file
        print("  [WARNING] Could not parse file blocks — saving as single file.")
        files = {"generated_code.txt": raw_output}

    print(f"  Files generated: {len(files)}")
    for name in files:
        print(f"    - {name}")

    # ── Step 5: Save files ────────────────────────────────────────
    print(f"\n[4/4] Saving files to '{output_dir}/'...")

    saved_paths = save_files(files, output_dir)

    for path in saved_paths:
        print(f"  ✓ {path}")

    print("\n" + "=" * 60)
    print("  Code generation complete!")
    print("=" * 60 + "\n")

    return {
        "owasp_domains": owasp_domains,
        "mitre_threats": mitre_threats,
        "security_context": combined_context,
        "raw_output": raw_output,
        "files": files,
        "saved_paths": saved_paths
    }
