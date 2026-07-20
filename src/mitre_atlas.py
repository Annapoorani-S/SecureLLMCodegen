"""
mitre_atlas.py

MITRE ATLAS Knowledge Base for AI/ML-Specific Threats.

MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)
documents adversarial attack techniques targeting AI/ML systems.

This module stores the ATLAS technique catalogue inline.
Each entry contains:
  - id        : ATLAS Technique ID
  - name      : Technique name
  - tactic    : ATLAS Tactic the technique belongs to
  - keywords  : Keywords that trigger this technique from a user requirement
  - mitigation: Defensive mitigations to inject into the security prompt

Reference: https://atlas.mitre.org/techniques
"""

# ------------------------------------------------------------------
# MITRE ATLAS Technique Catalogue
# ------------------------------------------------------------------

MITRE_ATTACKS = [
    {
        "id": "AML.T0051",
        "name": "Prompt Injection",
        "tactic": "ML Attack Staging",
        "keywords": [
            "chatbot", "llm", "gpt", "prompt", "chat",
            "assistant", "ai agent", "language model",
            "generative ai", "rag", "retrieval"
        ],
        "mitigation": [
            "Treat all user-supplied prompt content as untrusted input.",
            "Never allow user input to override system instructions.",
            "Sanitize and validate prompt content before processing.",
            "Use a separate privileged instruction channel for system prompts.",
            "Implement output filtering to prevent sensitive data leakage.",
            "Log and monitor all prompt inputs for anomalous patterns."
        ]
    },
    {
        "id": "AML.T0006",
        "name": "Jailbreak",
        "tactic": "ML Attack Staging",
        "keywords": [
            "chatbot", "llm", "gpt", "chat", "assistant",
            "language model", "generative ai", "ai model"
        ],
        "mitigation": [
            "Define strict model persona boundaries that cannot be overridden.",
            "Apply content filtering on model inputs and outputs.",
            "Use Constitutional AI or RLHF-based safety alignment.",
            "Reject or flag requests that attempt to change model identity.",
            "Rate-limit user interactions and log anomalous patterns."
        ]
    },
    {
        "id": "AML.T0048",
        "name": "Model Inversion Attack",
        "tactic": "Exfiltration",
        "keywords": [
            "train", "training data", "model", "inference",
            "prediction api", "ml model", "machine learning",
            "neural network", "deep learning"
        ],
        "mitigation": [
            "Apply differential privacy during model training.",
            "Limit the number of queries per user/session.",
            "Add noise to model predictions.",
            "Do not return confidence scores unless necessary.",
            "Monitor for repetitive queries targeting specific outputs."
        ]
    },
    {
        "id": "AML.T0049",
        "name": "Membership Inference Attack",
        "tactic": "Exfiltration",
        "keywords": [
            "train", "training data", "model", "inference",
            "machine learning", "ml model", "dataset",
            "personal data", "pii"
        ],
        "mitigation": [
            "Apply differential privacy to the training process.",
            "Do not expose whether a data point was used in training.",
            "Limit overfitting by using regularization techniques.",
            "Restrict API access to authorized users only.",
            "Implement query rate limiting and anomaly detection."
        ]
    },
    {
        "id": "AML.T0020",
        "name": "Data Poisoning",
        "tactic": "ML Attack Staging",
        "keywords": [
            "train", "training", "fine-tune", "finetune", "dataset",
            "labeling", "data collection", "feedback loop",
            "rlhf", "reinforcement learning"
        ],
        "mitigation": [
            "Validate and sanitize all training data before use.",
            "Implement data provenance tracking.",
            "Use anomaly detection to identify poisoned samples.",
            "Apply adversarial training techniques.",
            "Restrict who can contribute to training datasets.",
            "Monitor model performance for unexpected degradation."
        ]
    },
    {
        "id": "AML.T0034",
        "name": "Model Evasion",
        "tactic": "ML Attack Staging",
        "keywords": [
            "classifier", "detection", "spam filter", "fraud detection",
            "anomaly detection", "image classifier", "model", "prediction"
        ],
        "mitigation": [
            "Use adversarial training to increase model robustness.",
            "Apply input preprocessing to detect adversarial perturbations.",
            "Implement ensemble methods to reduce evasion success rates.",
            "Monitor input distributions for anomalous patterns.",
            "Use certified defenses where robustness guarantees are needed."
        ]
    },
    {
        "id": "AML.T0044",
        "name": "Model Theft / Extraction",
        "tactic": "Exfiltration",
        "keywords": [
            "api", "model api", "ml model", "prediction api",
            "inference api", "machine learning", "deep learning",
            "neural network", "model endpoint"
        ],
        "mitigation": [
            "Implement API rate limiting and per-user query quotas.",
            "Require authentication for all model API endpoints.",
            "Add watermarks to model outputs for traceability.",
            "Monitor query patterns for systematic extraction attempts.",
            "Use API gateway with anomaly detection.",
            "Do not expose model internals or confidence scores unnecessarily."
        ]
    },
    {
        "id": "AML.T0018",
        "name": "Backdoor ML Model",
        "tactic": "ML Attack Staging",
        "keywords": [
            "train", "fine-tune", "finetune", "pretrained", "model",
            "transfer learning", "open source model", "huggingface"
        ],
        "mitigation": [
            "Audit pre-trained models before deploying in production.",
            "Use models only from trusted and verified sources.",
            "Perform neural cleanse or similar backdoor detection.",
            "Validate model behaviour on clean test sets after fine-tuning.",
            "Track model lineage and version provenance."
        ]
    },
    {
        "id": "AML.T0057",
        "name": "LLM Plugin / Tool Abuse",
        "tactic": "Execution",
        "keywords": [
            "tool", "plugin", "function calling", "agent",
            "ai agent", "autonomous", "action", "execute",
            "code interpreter", "langchain", "autogpt"
        ],
        "mitigation": [
            "Restrict which tools and APIs an AI agent can invoke.",
            "Require explicit user confirmation for high-risk actions.",
            "Sandbox agent execution environments.",
            "Validate all tool inputs and outputs.",
            "Log all agent actions with full audit trail.",
            "Apply least-privilege principle to agent capabilities."
        ]
    },
    {
        "id": "AML.T0012",
        "name": "ML Supply Chain Compromise",
        "tactic": "Initial Access",
        "keywords": [
            "dependency", "package", "library", "huggingface",
            "pretrained", "open source", "model weight",
            "pip", "npm", "requirements"
        ],
        "mitigation": [
            "Pin dependency versions and use lock files.",
            "Verify checksums of downloaded model weights.",
            "Use private package mirrors where possible.",
            "Scan dependencies with vulnerability scanners.",
            "Audit third-party ML libraries before use.",
            "Sign and verify model artifacts."
        ]
    },
    {
        "id": "AML.T0068",
        "name": "AI System Exfiltration",
        "tactic": "Exfiltration",
        "keywords": [
            "model", "weights", "embedding", "vector",
            "vector store", "rag", "knowledge base",
            "system prompt", "configuration"
        ],
        "mitigation": [
            "Protect model weights and system prompts as sensitive assets.",
            "Restrict access to model files to authorized personnel only.",
            "Encrypt model weights at rest and in transit.",
            "Monitor file access and API calls for exfiltration patterns.",
            "Never expose system prompts in API responses.",
            "Apply DLP controls to model serving infrastructure."
        ]
    },
    {
        "id": "T1078",
        "name": "Valid Accounts Abuse",
        "tactic": "Initial Access",
        "keywords": [
            "login", "authentication", "jwt", "oauth",
            "password", "credential", "session", "token",
            "account", "user account", "sign in", "signin",
            "hotel", "booking", "reservation", "guest",
            "management", "dashboard", "portal", "admin",
            "staff", "member", "receptionist"
        ],
        "mitigation": [
            "Use strong password hashing (bcrypt or Argon2id).",
            "Enable Multi-Factor Authentication (MFA).",
            "Rate-limit login attempts and implement account lockout.",
            "Store secrets and credentials in environment variables.",
            "Validate JWT signatures and expiration on every request."
        ]
    },
    {
        "id": "T1110",
        "name": "Brute Force",
        "tactic": "Credential Access",
        "keywords": [
            "login", "password", "authentication", "signin",
            "sign in", "account", "hotel", "booking", "portal"
        ],
        "mitigation": [
            "Implement account lockout after repeated failed attempts.",
            "Apply CAPTCHA on login endpoints.",
            "Apply progressive delays between failed attempts.",
            "Log and alert on repeated failed login attempts.",
            "Rate-limit authentication endpoints."
        ]
    },
    {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "keywords": [
            "api", "rest", "express", "fastapi",
            "spring", "flask", "django", "backend", "server",
            "frontend", "front end", "front-end",
            "web app", "web application", "ui", "user interface",
            "html", "javascript", "react", "vue", "angular",
            "hotel", "hotel management", "management system",
            "booking", "reservation", "dashboard", "portal",
            "erp", "crm", "saas", "platform", "application"
        ],
        "mitigation": [
            "Validate and sanitize all user input on the server side.",
            "Keep all dependencies and frameworks up to date.",
            "Use HTTPS with valid TLS certificates.",
            "Implement authentication on all non-public endpoints.",
            "Apply Web Application Firewall (WAF) rules.",
            "Use a vulnerability scanner in your CI/CD pipeline.",
            "Apply security headers: CSP, X-Frame-Options, HSTS."
        ]
    }
]