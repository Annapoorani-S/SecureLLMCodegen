"""
mitre_context.py

MITRE ATLAS Context Builder.

Detects AI/ML-specific threats from a user requirement and builds a
formatted security context string to inject into the LLM prompt.

Public API:
    detect_ai_threats(requirement: str) -> list[str]
    build_mitre_context(requirement: str) -> str
"""

from src.mitre_atlas import MITRE_ATTACKS


# ------------------------------------------------------------------
# Threat Detection
# ------------------------------------------------------------------

def detect_ai_threats(requirement: str) -> list[str]:
    """
    Detect relevant MITRE ATLAS threats from a plain-English requirement.

    Args:
        requirement: The user's software requirement.

    Returns:
        A list of matched ATLAS technique names.
    """

    requirement_lower = requirement.lower()

    matched = []
    seen_ids = set()

    for attack in MITRE_ATTACKS:
        if attack["id"] in seen_ids:
            continue

        keywords = attack.get("keywords", [])

        if any(keyword.lower() in requirement_lower for keyword in keywords):
            matched.append(attack["name"])
            seen_ids.add(attack["id"])

    return matched


# ------------------------------------------------------------------
# Context Builder
# ------------------------------------------------------------------

def build_mitre_context(requirement: str) -> str:
    """
    Build a formatted MITRE ATLAS security context from a requirement.

    Args:
        requirement: User's software requirement.

    Returns:
        A formatted string containing ATLAS mitigations to inject
        into the LLM security prompt. Returns an empty string if
        no threats are detected.
    """

    requirement_lower = requirement.lower()

    context = []
    seen_ids = set()

    for attack in MITRE_ATTACKS:
        if attack["id"] in seen_ids:
            continue

        keywords = attack.get("keywords", [])

        if not any(keyword.lower() in requirement_lower for keyword in keywords):
            continue

        seen_ids.add(attack["id"])

        context.append(f"## {attack['name']}")
        context.append(f"MITRE ATLAS Technique: {attack['id']} | Tactic: {attack['tactic']}")
        context.append("")

        for mitigation in attack["mitigation"]:
            context.append(f"- {mitigation}")

        context.append("")

    if not context:
        return ""

    header = [
        "### MITRE ATLAS – AI/ML Threat Mitigations",
        "",
        "Apply the following AI-specific security measures:",
        ""
    ]

    return "\n".join(header + context)
