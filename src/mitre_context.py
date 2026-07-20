"""
MITRE ATLAS Context Builder
"""

MITRE_RULES = {
    "chatbot": {
        "title": "Prompt Injection",
        "guidelines": [
            "Treat all user prompts as untrusted input.",
            "Never execute arbitrary instructions from users.",
            "Validate and sanitize prompt content."
        ]
    },

    "llm": {
        "title": "Model Abuse",
        "guidelines": [
            "Limit model capabilities.",
            "Protect system prompts.",
            "Restrict sensitive operations."
        ]
    },

    "ai": {
        "title": "AI Security",
        "guidelines": [
            "Protect against prompt injection.",
            "Avoid exposing sensitive information.",
            "Validate generated outputs."
        ]
    }
}
def build_mitre_context(requirement: str) -> str:

    requirement = requirement.lower()

    context = []

    for keyword, info in MITRE_RULES.items():

        if keyword in requirement:

            context.append(f"## {info['title']}")

            for rule in info["guidelines"]:

                context.append(f"- {rule}")

    return "\n".join(context)
import json
from pathlib import Path

# Locate attacks.json
BASE_DIR = Path(__file__).resolve().parent.parent
ATTACKS_FILE = BASE_DIR / "knowledge_base" / "mitre" / "attacks.json"

# Load the MITRE rules
with open(ATTACKS_FILE, "r", encoding="utf-8") as f:
    MITRE_ATTACKS = json.load(f)
def build_mitre_context(requirement: str) -> str:
    requirement = requirement.lower()

    context = []

    for attack in MITRE_ATTACKS:

        keywords = attack.get("keywords", [])

        if any(keyword.lower() in requirement for keyword in keywords):

            context.append(f"## {attack['name']}")
            context.append(f"MITRE Technique: {attack['id']}")

            for mitigation in attack["mitigation"]:
                context.append(f"- {mitigation}")

            context.append("")

    return "\n".join(context)
