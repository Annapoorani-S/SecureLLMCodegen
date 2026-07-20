"""
main.py

AISAF – AI Secure Architecture Framework
Entry point for the secure code generation pipeline.

Usage:
    # Interactive mode (will prompt for requirement):
    python main.py

    # Pass requirement directly as argument:
    python main.py --requirement "Build a Flask JWT login API with PostgreSQL"

    # Specify output directory:
    python main.py --requirement "..." --output my_project/

    # Preview security context only (no code generation):
    python main.py --requirement "..." --dry-run
"""

import argparse
import sys

from src.pipeline import run_pipeline, build_combined_context


# ------------------------------------------------------------------
# CLI Argument Parser
# ------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aisaf",
        description=(
            "AISAF – AI Secure Architecture Framework\n"
            "Generates secure, production-ready code with OWASP + MITRE ATLAS guidance."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--requirement", "-r",
        type=str,
        default=None,
        help="Natural language software requirement."
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Directory to save generated files (default: output/)."
    )

    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Print the security context only - do not call Groq or save files."
    )

    return parser.parse_args()


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # ── Get requirement ───────────────────────────────────────────
    requirement = args.requirement

    if not requirement:
        print("\n" + "=" * 60)
        print("  AISAF – AI Secure Architecture Framework")
        print("  Powered by OWASP Top 10 + MITRE ATLAS")
        print("=" * 60)
        print()
        print("Enter your software requirement (press Enter twice when done):")
        print()

        lines = []
        try:
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Cancelled.")
            sys.exit(0)

        requirement = "\n".join(lines).strip()

    if not requirement:
        print("[ERROR] No requirement provided. Exiting.")
        sys.exit(1)

    # ── Dry run: just show security context ───────────────────────
    if args.dry_run:
        print("\n" + "=" * 60)
        print("  DRY RUN – Security Context Preview")
        print("=" * 60)

        combined_context, owasp_domains, mitre_threats = build_combined_context(requirement)

        print(f"\nOWASP Domains   : {', '.join(owasp_domains)}")
        print(f"MITRE Threats   : {', '.join(mitre_threats) if mitre_threats else 'None detected'}")
        print("\n--- Combined Security Context ---\n")
        print(combined_context)
        return

    # ── Full pipeline ─────────────────────────────────────────────
    try:
        result = run_pipeline(
            requirement=requirement,
            output_dir=args.output
        )

        print(f"\nSummary:")
        print(f"  OWASP domains : {', '.join(result['owasp_domains'])}")
        print(f"  MITRE threats : {', '.join(result['mitre_threats']) if result['mitre_threats'] else 'None'}")
        print(f"  Files saved   : {len(result['saved_paths'])}")
        print(f"  Output folder : {args.output}/\n")

    except RuntimeError as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
