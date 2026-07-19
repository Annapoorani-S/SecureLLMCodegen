"""
llm_client.py

Gemini client responsible for:

1. Generating secure code from natural language requirements.
2. Fixing vulnerabilities detected by security scanners.

Architecture:

Requirement
      |
      v
Security Context
      |
      v
Gemini Secure Code Generator
      |
      v
Generated Code


Scanner Findings
      |
      v
Gemini Security Fix Agent
      |
      v
Fixed Code
"""

import json
import re
import time

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL


# ==========================================================
# Gemini Client
# ==========================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ==========================================================
# Secure Code Generation Prompt
# ==========================================================

GENERATE_SYSTEM_PROMPT = """

You are an expert Secure Software Architect and Senior Software Engineer.

Your task is to generate secure, production-ready software from a natural language requirement.

The generated solution may use any programming language or framework requested by the user.

Supported technologies include (but are not limited to):

- Python
- Java
- JavaScript
- TypeScript
- Go
- C#
- Rust
- PHP
- Kotlin
- Swift
- Spring Boot
- FastAPI
- Flask
- Django
- Express.js
- NestJS
- React
- Angular
- Vue
- Docker
- Kubernetes
- Terraform
- AWS
- Azure
- GCP

----------------------------------------------------
SECURE CODING REQUIREMENTS
----------------------------------------------------

Always:

1. Detect the required programming language.
2. Detect the required framework.
3. If none is specified, choose the best technology.
4. Apply OWASP Top 10 secure coding principles.
5. Never hardcode secrets.
6. Use environment variables.
7. Validate every external input.
8. Prevent SQL Injection.
9. Prevent XSS.
10. Prevent CSRF where applicable.
11. Prevent SSRF.
12. Implement secure authentication.
13. Implement authorization.
14. Apply least privilege.
15. Handle errors securely.
16. Log security events.
17. Use secure cryptography.
18. Use parameterized queries.
19. Follow production-ready coding practices.

----------------------------------------------------
PROJECT GENERATION RULE
----------------------------------------------------

Generate the COMPLETE project.

Include EVERY required file.

Examples:

Python:
- requirements.txt
- app.py
- main.py
- routes/
- models/
- services/
- config/
- README.md
- .env.example

Node.js:
- package.json
- server.js
- src/
- routes/
- middleware/
- controllers/
- models/
- config/
- README.md
- .env.example

Java:
- pom.xml
- src/main/java/...
- src/main/resources/application.properties
- README.md
- Dockerfile (if appropriate)

Go:
- go.mod
- main.go
- internal/
- README.md

Rust:
- Cargo.toml
- src/main.rs

----------------------------------------------------
OUTPUT FORMAT
----------------------------------------------------

Return EVERY file using EXACTLY this format:

=== FILE: package.json ===
<contents>

=== FILE: src/server.js ===
<contents>

=== FILE: src/routes/auth.js ===
<contents>

=== FILE: README.md ===
<contents>

Do NOT skip files.

Do NOT summarize.

Do NOT explain.

Return ONLY the project files.

----------------------------------------------------
SECURITY GUIDELINES
----------------------------------------------------

{security_context}

"""


# ==========================================================
# Vulnerability Fix Prompt
# ==========================================================

FIX_SYSTEM_PROMPT = """

You are a senior application security engineer.

Your task is to fix security vulnerabilities in source code.

You will receive:

1. Existing source code.
2. Security scanner findings.

Your responsibilities:

- Fix every reported vulnerability.
- Preserve existing functionality.
- Do not remove required features.
- Do not introduce new vulnerabilities.
- Apply OWASP secure coding practices.
- Improve security where necessary.

IMPORTANT OUTPUT RULE:

Return ONLY the corrected complete source code.

No explanations.
No markdown outside the code block.

Security Findings:

{findings_json}

"""


# ==========================================================
# Utility Functions
# ==========================================================

def _check_client():

    if client is None:
        raise RuntimeError(
            "Gemini API key missing. "
            "Add GEMINI_API_KEY to .env"
        )


def _extract_code_block(text: str) -> str:
    """
    Extract code from markdown fences.

    Example:

    ```python
    print("hello")
    ```

    becomes:

    print("hello")
    """

    pattern = r"""
    ```[\w+-]*
    (.*?)
    ```
    """

    match = re.search(
        pattern,
        text,
        re.DOTALL | re.VERBOSE
    )

    if match:
        return match.group(1).strip()

    return text.strip()


# ==========================================================
# Gemini API Call Wrapper
# ==========================================================

def _call_gemini(
    system_prompt: str,
    user_content: str
) -> str:

    _check_client()

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_content,
            config={
                "system_instruction": system_prompt,
                "max_output_tokens": 5000,
                "temperature": 0.2
            }
        )

        return response.text


    except Exception as error:

        error_message = str(error)


        # Better quota handling

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

            raise RuntimeError(
                """
Gemini API quota exceeded.

Possible fixes:
1. Wait for quota reset.
2. Enable billing.
3. Use another Gemini project/API key.
4. Try another available model.
"""
            )


        raise error



# ==========================================================
# Generate Code
# ==========================================================

def generate_code(
    requirement: str,
    security_context: str
) -> str:
    """
    Generate secure source code.

    Args:

        requirement:
            User software requirement.

        security_context:
            OWASP security rules.

    Returns:

        Generated source code.
    """


    system_prompt = GENERATE_SYSTEM_PROMPT.format(
        security_context=security_context
    )


    response = _call_gemini(
        system_prompt,
        requirement
    )


    return _extract_code_block(response)



# ==========================================================
# Fix Vulnerable Code
# ==========================================================

def fix_code(
    code: str,
    findings: list
) -> str:
    """
    Fix vulnerabilities detected by scanners.
    """


    findings_json = json.dumps(
        findings,
        indent=2
    )


    system_prompt = FIX_SYSTEM_PROMPT.format(
        findings_json=findings_json
    )


    user_content = (
        "Fix this source code:\n\n"
        "```code\n"
        f"{code}\n"
        "```"
    )


    response = _call_gemini(
        system_prompt,
        user_content
    )


    return _extract_code_block(response)