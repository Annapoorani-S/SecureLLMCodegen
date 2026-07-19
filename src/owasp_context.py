"""
owasp_context.py

Provides security guidance based on the user's software requirement.

This module stores OWASP-aligned secure coding knowledge that will
be injected into the LLM prompt before code generation.

NOTE:
Later in this project, we will add:
- KEYWORD_MAP
- detect_security_domains()
- build_security_context()
"""

SECURITY_GUIDELINES = {
    "authentication": {
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "description": "Secure authentication and credential management.",
        "guidelines": [
            "Hash passwords using Argon2id or bcrypt.",
            "Never store plaintext passwords.",
            "Use Multi-Factor Authentication (MFA) where appropriate.",
            "Validate JWT signatures and expiration before trusting claims.",
            "Implement rate limiting on authentication endpoints.",
            "Use secure session management.",
            "Store secrets in environment variables.",
            "Return generic authentication error messages."
        ]
    },

    "authorization": {
        "owasp": "A01:2021 - Broken Access Control",
        "description": "Ensure authenticated users can access only permitted resources.",
        "guidelines": [
            "Always verify user permissions on the server.",
            "Never trust client-side authorization.",
            "Enforce least privilege.",
            "Validate ownership before returning or modifying resources.",
            "Implement Role-Based Access Control (RBAC) where appropriate."
        ]
    },

    "input_validation": {
        "owasp": "A03:2021 - Injection",
        "description": "Validate every external input before processing.",
        "guidelines": [
            "Validate type, format and length.",
            "Reject unexpected characters.",
            "Prefer allow-lists over block-lists.",
            "Validate request headers, query parameters and request bodies."
        ]
    },

    "sql_injection": {
        "owasp": "A03:2021 - Injection",
        "description": "Prevent SQL Injection attacks.",
        "guidelines": [
            "Always use parameterized queries or prepared statements.",
            "Never concatenate user input into SQL queries.",
            "Use ORM features safely.",
            "Use least-privilege database accounts.",
            "Never expose SQL errors to users."
        ]
    },

    "file_upload": {
        "owasp": "A05:2021 - Security Misconfiguration",
        "description": "Secure handling of uploaded files.",
        "guidelines": [
            "Validate file extensions.",
            "Validate MIME types.",
            "Rename uploaded files.",
            "Limit maximum upload size.",
            "Prevent path traversal attacks.",
            "Store uploads outside the web root.",
            "Scan uploaded files whenever possible."
        ]
    },

    "ssrf": {
        "owasp": "A10:2021 - Server-Side Request Forgery",
        "description": "Protect applications from SSRF attacks.",
        "guidelines": [
            "Use an allow-list of trusted domains.",
            "Block localhost and private IP ranges.",
            "Validate URLs before making requests.",
            "Disable unnecessary redirects.",
            "Use outbound network restrictions where possible."
        ]
    },

    "deserialization": {
        "owasp": "A08:2021 - Software and Data Integrity Failures",
        "description": "Prevent insecure deserialization.",
        "guidelines": [
            "Never deserialize untrusted data.",
            "Avoid pickle for untrusted input.",
            "Avoid eval() on user-controlled input.",
            "Prefer JSON over binary serialization.",
            "Validate serialized content before processing."
        ]
    },

    "cryptography": {
        "owasp": "A02:2021 - Cryptographic Failures",
        "description": "Protect sensitive data using strong cryptography.",
        "guidelines": [
            "Use modern cryptographic algorithms.",
            "Never implement custom encryption.",
            "Encrypt sensitive data at rest.",
            "Encrypt sensitive data in transit using TLS.",
            "Rotate encryption keys periodically."
        ]
    },

    "secrets_management": {
        "owasp": "A02:2021 - Cryptographic Failures",
        "description": "Secure management of secrets and credentials.",
        "guidelines": [
            "Never hardcode secrets.",
            "Store secrets in environment variables or a secret manager.",
            "Rotate credentials regularly.",
            "Use different credentials for each environment."
        ]
    },

    "api_security": {
        "owasp": "OWASP API Security Top 10",
        "description": "General secure API development practices.",
        "guidelines": [
            "Authenticate every protected endpoint.",
            "Validate every request.",
            "Apply least privilege.",
            "Enable CORS only for trusted origins.",
            "Return generic error messages.",
            "Log important security events.",
            "Implement rate limiting.",
            "Use HTTPS for all communications."
        ]
    }
}

# -------------------------------------------------------------------
# Keywords used to identify relevant security domains
# -------------------------------------------------------------------

KEYWORD_MAP = {
    "authentication": [
        "login",
        "signin",
        "signup",
        "register",
        "password",
        "authenticate",
        "authentication",
        "jwt",
        "oauth",
        "token",
    ],

    "authorization": [
        "admin",
        "role",
        "permission",
        "access",
        "authorize",
        "authorization",
        "user id",
        "profile",
    ],

    "input_validation": [
        "input",
        "form",
        "request",
        "user input",
        "query parameter",
        "body",
        "validation",
    ],

    "sql_injection": [
        "database",
        "sql",
        "mysql",
        "postgres",
        "sqlite",
        "query",
        "search",
        "filter",
    ],

    "file_upload": [
        "upload",
        "file",
        "image",
        "avatar",
        "document",
        "profile picture",
    ],

    "ssrf": [
        "url",
        "fetch",
        "download",
        "proxy",
        "remote",
        "external api",
    ],

    "deserialization": [
        "deserialize",
        "serialization",
        "pickle",
        "unpickle",
    ],

    "cryptography": [
        "encrypt",
        "decrypt",
        "certificate",
        "tls",
        "ssl",
        "crypto",
    ],

    "secrets_management": [
        "secret",
        "apikey",
        "api key",
        "credential",
        "environment variable",
        "password storage",
    ],

    "api_security": [
        "api",
        "endpoint",
        "rest",
        "service",
        "backend",
    ],
}
def detect_security_domains(requirement: str) -> list[str]:
    """
    Detect relevant security domains from a plain-English requirement.

    Args:
        requirement: The user's software requirement.

    Returns:
        A list of matching security domain names.
    """

    requirement = requirement.lower()

    matched_domains = set()

    for domain, keywords in KEYWORD_MAP.items():

        for keyword in keywords:

            if keyword.lower() in requirement:
                matched_domains.add(domain)

    if not matched_domains:
        matched_domains.add("api_security")

    return sorted(matched_domains)

def build_security_context(requirement: str) -> str:
    """
    Build a formatted security context based on the detected security domains.

    Args:
        requirement: User's software requirement.

    Returns:
        A formatted string containing relevant security guidance.
    """

    domains = detect_security_domains(requirement)

    context = [
        "### Security Guidelines",
        "",
        "Apply the following secure coding practices while generating the code:",
        ""
    ]

    for domain in domains:

        info = SECURITY_GUIDELINES.get(domain)

        if not info:
            continue

        context.append(f"## {domain.replace('_', ' ').title()}")
        context.append(f"OWASP: {info['owasp']}")
        context.append(info["description"])
        context.append("")

        for guideline in info["guidelines"]:
            context.append(f"- {guideline}")

        context.append("")

    return "\n".join(context)