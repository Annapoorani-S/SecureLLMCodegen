"""
tests/test_owasp.py

Unit tests for the OWASP Context Engine.
No Groq API key required - tests are purely local.
"""

import pytest
from src.owasp_context import detect_security_domains, build_security_context


# ------------------------------------------------------------------
# detect_security_domains() tests
# ------------------------------------------------------------------

class TestDetectSecurityDomains:

    def test_authentication_keywords(self):
        domains = detect_security_domains("Build a login API with JWT tokens")
        assert "authentication" in domains

    def test_sql_injection_keywords(self):
        domains = detect_security_domains("Search products in MySQL database")
        assert "sql_injection" in domains

    def test_file_upload_keywords(self):
        domains = detect_security_domains("Allow users to upload profile pictures")
        assert "file_upload" in domains

    def test_api_security_fallback(self):
        """Completely unrelated requirement should still get api_security."""
        domains = detect_security_domains("Tell me a joke")
        assert "api_security" in domains

    def test_multiple_domains(self):
        """A rich requirement should trigger multiple domains."""
        req = "Build a REST API with JWT login and PostgreSQL database"
        domains = detect_security_domains(req)
        assert "authentication" in domains
        assert "sql_injection" in domains
        assert "api_security" in domains

    def test_returns_sorted_list(self):
        domains = detect_security_domains("login register api database")
        assert domains == sorted(domains)

    def test_case_insensitive(self):
        domains = detect_security_domains("BUILD A LOGIN API WITH DATABASE")
        assert "authentication" in domains

    def test_ssrf_keywords(self):
        domains = detect_security_domains("Fetch data from an external API URL")
        assert "ssrf" in domains

    def test_cryptography_keywords(self):
        domains = detect_security_domains("Encrypt user data with TLS")
        assert "cryptography" in domains

    def test_secrets_management(self):
        domains = detect_security_domains("Store API keys and credentials securely")
        assert "secrets_management" in domains


# ------------------------------------------------------------------
# build_security_context() tests
# ------------------------------------------------------------------

class TestBuildSecurityContext:

    def test_returns_string(self):
        ctx = build_security_context("Build a login API")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_contains_owasp_reference(self):
        ctx = build_security_context("Build a login API with JWT")
        assert "OWASP" in ctx

    def test_contains_domain_name(self):
        ctx = build_security_context("Build a login API")
        assert "Authentication" in ctx

    def test_contains_guidelines(self):
        ctx = build_security_context("Build a login API")
        # Guidelines are formatted as bullet points
        assert "- " in ctx

    def test_sql_context_contains_parameterized(self):
        ctx = build_security_context("Search products in database with SQL")
        assert "parameterized" in ctx.lower()

    def test_file_upload_context(self):
        ctx = build_security_context("Upload user profile pictures")
        assert "path traversal" in ctx.lower() or "mime" in ctx.lower()

    def test_empty_requirement_gets_fallback(self):
        ctx = build_security_context("")
        # Should still return something (falls back to api_security)
        assert len(ctx) > 0
