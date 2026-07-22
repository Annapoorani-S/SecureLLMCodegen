"""
prompt_builder.py

AISAF Prompt Builder

Builds a structured security-aware prompt for the LLM.
"""

from src.tech_classifier import classify_technology


def build_prompt(
    requirement: str,
    owasp_context: str,
    mitre_context: str
) -> str:
    """
    Build a complete secure prompt for the LLM.
    """

    tech = classify_technology(requirement)

    prompt = f"""
You are an expert Secure Software Architect.

Generate production-ready secure code.

==================================================
PROJECT REQUIREMENT
==================================================

{requirement}

==================================================
TECHNOLOGY STACK
==================================================

Language : {tech["language"]}
Framework: {tech["framework"]}
Database : {tech["database"]}
Frontend : {tech["frontend"]}
Project  : {tech["project_type"]}

==================================================
OWASP SECURITY REQUIREMENTS
==================================================

{owasp_context}

==================================================
MITRE ATLAS REQUIREMENTS
==================================================

{mitre_context}

==================================================
CODING RULES
==================================================

1. Follow secure coding practices.
2. Prevent SQL Injection.
3. Validate all user inputs.
4. Use parameterized queries.
5. Never hardcode secrets.
6. Implement authentication securely.
7. Return production-quality code.
8. Add comments where appropriate.

==================================================
OUTPUT FORMAT
==================================================

Return files exactly in this format.

=== FILE: app.py ===

<code>

=== FILE: requirements.txt ===

<content>

Do not include explanations.
Return only the files.
"""

    return prompt


if __name__ == "__main__":

    requirement = """
    Build a Flask banking REST API using PostgreSQL.
    """

    owasp = """
Use parameterized queries.
Validate inputs.
Use JWT Authentication.
"""

    mitre = """
Protect against Prompt Injection.
Protect against Data Leakage.
"""

    print(build_prompt(requirement, owasp, mitre))