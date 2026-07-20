"""
llm_client.py

Groq client responsible for:

1. Generating secure code from natural language requirements.
2. Fixing vulnerabilities detected by security scanners.

Architecture:

Requirement
      |
      v
Security Context
      |
      v
Groq Secure Code Generator
      |
      v
Generated Code


Scanner Findings
      |
      v
Groq Security Fix Agent
      |
      v
Fixed Code
"""

import json
import random
import re
import time

from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL


# ==========================================================
# Model Fallback Chain
# ==========================================================
# If the primary model hits quota, the client automatically
# retries with the next model in this list.
MODEL_FALLBACK_CHAIN = [
    GROQ_MODEL,                 # from .env (default: llama-3.3-70b-versatile)
    "openai/gpt-oss-120b",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
]

# Deduplicate while preserving order (in case .env model is already in list)
_seen = set()
_MODEL_CHAIN: list[str] = []
for _m in MODEL_FALLBACK_CHAIN:
    if _m not in _seen:
        _seen.add(_m)
        _MODEL_CHAIN.append(_m)


# ==========================================================
# Groq Client
# ==========================================================

client = None

if GROQ_API_KEY:
    client = Groq(
        api_key=GROQ_API_KEY
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
            "Groq API key missing. "
            "Add GROQ_API_KEY to .env"
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
# Groq API Call Wrapper
# ==========================================================

def _call_groq(
    system_prompt: str,
    user_content: str,
    max_retries: int = 3,
) -> str:
    """
    Call the Groq API with exponential-backoff retry and model fallback.

    Retry strategy:
      - On quota / rate-limit errors (HTTP 429 / RESOURCE_EXHAUSTED):
          1. Wait with exponential backoff + jitter.
          2. After all retries on the current model are exhausted,
             fall back to the next model in _MODEL_CHAIN.
      - On any other error: raise immediately.

    Args:
        system_prompt: System instruction for the model.
        user_content:  User message / requirement.
        max_retries:   Retry attempts per model before falling back.

    Returns:
        Model response text.
    """

    _check_client()

    last_error: Exception | None = None

    for model in _MODEL_CHAIN:

        for attempt in range(1, max_retries + 1):

            try:
                print(f"  [Groq] Using model: {model} (attempt {attempt}/{max_retries})")

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    max_tokens=8192,
                    temperature=0.2,
                )

                content = response.choices[0].message.content
                if isinstance(content, list):
                    return "\n".join(
                        part.get("text", "")
                        if isinstance(part, dict)
                        else str(part)
                        for part in content
                    ).strip()

                return (content or "").strip()

            except Exception as error:

                error_message = str(error)
                last_error = error

                is_quota_error = (
                    "429" in error_message
                    or "RESOURCE_EXHAUSTED" in error_message
                    or "quota" in error_message.lower()
                    or "rate" in error_message.lower()
                )

                if not is_quota_error:
                    # Non-quota error — fail immediately
                    raise error

                if attempt < max_retries:
                    # Exponential backoff with jitter: 2^attempt * (0.8–1.2)
                    wait = (2 ** attempt) * random.uniform(0.8, 1.2)
                    print(
                        f"  [Groq] Quota limit on {model}. "
                        f"Retrying in {wait:.1f}s "
                        f"(attempt {attempt}/{max_retries})..."
                    )
                    time.sleep(wait)

                else:
                    print(
                        f"  [Groq] All {max_retries} retries exhausted on {model}. "
                        "Trying next model in fallback chain..."
                    )

    # Every model in the chain failed
    raise RuntimeError(
        "\n"
        "Groq API quota exceeded on ALL available models.\n"
        "\n"
        "Possible fixes:\n"
        "  1. Wait a few minutes for the per-minute quota to reset.\n"
        "  2. Check your Groq dashboard rate limits and billing settings.\n"
        "  3. Add a different GROQ_API_KEY to your .env file.\n"
        "  4. Set GROQ_MODEL=llama-3.1-8b-instant in .env for a faster fallback.\n"
        "\n"
        f"Last error: {last_error}"
    )



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


    response = _call_groq(
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


    response = _call_groq(
        system_prompt,
        user_content
    )


    return _extract_code_block(response)
