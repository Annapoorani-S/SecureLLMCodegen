"""
AISAF - Gemini LLM Client

Handles:
1. Secure code generation
2. Vulnerability fixing
3. Gemini API communication
"""

import os
import time

from dotenv import load_dotenv
from google import genai


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)


MODEL = "gemini-2.5-flash"



# ==================================================
# GEMINI REQUEST HANDLER
# ==================================================

def call_gemini(prompt, retries=2):

    if client is None:
        raise ValueError(
            "GEMINI_API_KEY not found. Add it to backend/.env before generating code."
        )

    for attempt in range(retries + 1):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )


            if response.text:

                return response.text


            return None


        except Exception as e:


            error = str(e)


            print(
                "\n[Gemini Error]",
            )

            print(error)



            # Quota exceeded

            if "RESOURCE_EXHAUSTED" in error:

                print(
                    "\nGemini quota exceeded."
                )

                print(
                    "Wait for quota reset."
                )

                return None



            # Retry temporary errors

            if attempt < retries:


                wait_time = 2 ** attempt


                print(
                    f"Retrying Gemini after {wait_time}s..."
                )


                time.sleep(
                    wait_time
                )


            else:

                return None



# ==================================================
# CODE GENERATION AGENT
# ==================================================

def generate_code(
        requirement,
        security_context
):


    print(
        "\n[Gemini] Generating secure project..."
    )



    prompt = """

You are AISAF.

AI Secure Architecture Framework.


Generate a complete secure software project.


User Requirement:

{requirement}



Security Context:

{security_context}



Rules:

- Follow OWASP Top 10
- Follow MITRE ATLAS security practices
- Use secure coding principles
- No hardcoded secrets
- Validate inputs
- Secure authentication
- Secure authorization
- Prevent SQL injection
- Prevent XSS
- Add proper error handling



Return ONLY JSON.


Required format:


{{
    "files":
    {{
        "filename":
        "file content"
    }}
}}


No markdown.
No explanations.

""".format(
        requirement=requirement,
        security_context=security_context
    )



    return call_gemini(
        prompt
    )




# ==================================================
# VULNERABILITY FIX AGENT
# ==================================================

def fix_vulnerable_code(
        code,
        security_issue
):


    print(
        "\n[Gemini Fix Agent] Analysing vulnerability..."
    )



    prompt = """

You are AISAF Vulnerability Fix Agent.


A security scanner detected a vulnerability.


Scanner:

{tool}


Rule:

{rule}


Severity:

{severity}


Message:

{message}



Affected Code:

----------------

{code}

----------------



Task:

Fix this vulnerability.

Requirements:

- Keep existing functionality
- Apply secure coding practices
- Remove vulnerability
- Return ONLY corrected source code


""".format(

        tool=security_issue.get(
            "tool"
        ),

        rule=security_issue.get(
            "rule"
        ),

        severity=security_issue.get(
            "severity"
        ),

        message=security_issue.get(
            "message"
        ),

        code=code

    )



    result = call_gemini(
        prompt
    )



    if result is None:

        print(
            "[Gemini Fix Failed] Keeping original code"
        )

        return code



    # Remove markdown if Gemini adds it

    result = result.replace(
        "```python",
        ""
    )


    result = result.replace(
        "```",
        ""
    )


    return result.strip()




# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":


    response = generate_code(

        """
        Create Flask REST API
        with JWT authentication
        and PostgreSQL.
        """,

        """
        OWASP:
        authentication,
        sql injection

        MITRE:
        credential abuse
        """

    )


    if response:

        print(
            response[:500]
        )

    else:

        print(
            "Gemini failed"
        )
