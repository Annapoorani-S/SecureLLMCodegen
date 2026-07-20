[
  {
    "id": "T1078",
    "name": "Valid Accounts",
    "keywords": [
      "login",
      "authentication",
      "jwt",
      "oauth",
      "password"
    ],
    "mitigation": [
      "Use strong password hashing (bcrypt or Argon2).",
      "Enable Multi-Factor Authentication.",
      "Rate limit login attempts.",
      "Store secrets in environment variables."
    ]
  },
  {
    "id": "T1110",
    "name": "Brute Force",
    "keywords": [
      "login",
      "password"
    ],
    "mitigation": [
      "Implement account lockout.",
      "Apply rate limiting.",
      "Log repeated failed login attempts."
    ]
  },
  {
    "id": "T1190",
    "name": "Exploit Public-Facing Application",
    "keywords": [
      "api",
      "rest",
      "express",
      "fastapi",
      "spring"
    ],
    "mitigation": [
      "Validate all user input.",
      "Keep dependencies updated.",
      "Use HTTPS.",
      "Implement authentication."
    ]
  }
]
]