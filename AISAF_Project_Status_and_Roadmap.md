# AISAF -- AI Secure Architecture Framework

## Project Status (Current)

### Objective

Build a security-aware AI code generation pipeline that augments LLM
prompts with OWASP secure coding guidance before generating code.

## Architecture

``` text
User Requirement
      |
      v
Security Domain Detection
      |
      v
OWASP Context Builder
      |
      v
Security Prompt Augmentation
      |
      v
Groq API
      |
      v
Secure Code Generation
```

## Components Implemented

### 1. OWASP Context Engine

-   Detects security-related keywords in user requirements.
-   Maps requirements to OWASP Top 10 / API Security guidance.
-   Builds a dynamic security context.

### 2. Security Prompt Augmentation

-   Injects the generated OWASP guidance into the Groq system prompt.
-   Ensures the model receives security requirements alongside the
    functional request.

### 3. Groq Client

-   Generates secure source code.
-   Supports security remediation through `fix_code()`.
-   Uses configurable model and API key.

### 4. Prompt Engineering

Current system prompt instructs Groq-hosted models to: - Produce production-ready
code. - Apply secure coding practices. - Avoid hardcoded secrets. -
Validate input. - Use environment variables. - Apply authentication and
authorization correctly.

## Validation Performed

-   Generated secure Flask JWT authentication API.
-   Generated secure Spring Boot banking backend.
-   Generated secure Express.js REST API.
-   Verified OWASP context generation for authentication, authorization,
    API security, and SQL injection.

## Current Limitations

-   Complete multi-file project generation is inconsistent.
-   No post-generation security validation yet.
-   No MITRE ATLAS integration yet.
-   No automated scanner integration.

# Roadmap

## Phase 2

-   Improve prompts for complete project generation.
-   Save generated projects into file structure.
-   Generate README, Dockerfile and configuration files consistently.

## Phase 3

-   Integrate MITRE ATLAS.
-   Detect AI-specific threats (prompt injection, model theft, data
    poisoning, jailbreaks).
-   Merge OWASP + MITRE guidance into one security context.

## Phase 4

-   Integrate security scanners (Promptfoo, Semgrep, Bandit, etc.).
-   Feed findings into `fix_code()` for automatic remediation.

## Phase 5

-   Build AISAF orchestration pipeline:
    1.  Requirement Analysis
    2.  Security Context Builder
    3.  Secure Code Generation
    4.  Security Validation
    5.  Automatic Remediation
    6.  Final Secure Project Output

## Vision

AISAF aims to become an AI Secure Software Architect that generates
secure software by default, validates the result, detects
vulnerabilities, remediates them automatically, and eventually
incorporates both traditional application security (OWASP) and
AI-specific security (MITRE ATLAS).
