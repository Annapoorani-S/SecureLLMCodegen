"""
tests/test_pipeline.py

Unit tests for the AISAF unified pipeline.

These tests cover:
  - build_combined_context() — no API key required
  - parse_generated_files()  — no API key required
  - run_pipeline() with a mocked Groq call - no real API key required
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.pipeline import build_combined_context, parse_generated_files, run_pipeline


# ------------------------------------------------------------------
# build_combined_context() tests
# ------------------------------------------------------------------

class TestBuildCombinedContext:

    def test_returns_tuple_of_three(self):
        result = build_combined_context("Build a login API")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_context_is_string(self):
        ctx, _, _ = build_combined_context("Build a login API")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_owasp_domains_is_list(self):
        _, owasp_domains, _ = build_combined_context("Build a login API")
        assert isinstance(owasp_domains, list)

    def test_mitre_threats_is_list(self):
        _, _, mitre_threats = build_combined_context("Build a login API")
        assert isinstance(mitre_threats, list)

    def test_owasp_context_present(self):
        ctx, owasp_domains, _ = build_combined_context("Build a login API with JWT")
        assert "OWASP" in ctx
        assert "authentication" in owasp_domains

    def test_mitre_context_present_for_ai(self):
        ctx, _, mitre_threats = build_combined_context(
            "Build a chatbot with LLM integration"
        )
        assert "MITRE ATLAS" in ctx
        assert len(mitre_threats) > 0

    def test_combined_context_includes_both_when_applicable(self):
        ctx, owasp_domains, mitre_threats = build_combined_context(
            "Build a chatbot with JWT login API using LLM and database"
        )
        assert "OWASP" in ctx
        assert "MITRE ATLAS" in ctx
        assert len(owasp_domains) > 0
        assert len(mitre_threats) > 0

    def test_plain_requirement_no_mitre(self):
        ctx, _, mitre_threats = build_combined_context("print hello world")
        # No AI/ML keywords → no MITRE threats
        assert mitre_threats == []
        assert "MITRE ATLAS" not in ctx


# ------------------------------------------------------------------
# parse_generated_files() tests
# ------------------------------------------------------------------

class TestParseGeneratedFiles:

    def test_single_file(self):
        raw = """
=== FILE: app.py ===
print("hello world")
"""
        files = parse_generated_files(raw)
        assert "app.py" in files
        assert 'print("hello world")' in files["app.py"]

    def test_multiple_files(self):
        raw = """
=== FILE: app.py ===
print("hello")

=== FILE: requirements.txt ===
flask>=2.0
"""
        files = parse_generated_files(raw)
        assert "app.py" in files
        assert "requirements.txt" in files
        assert len(files) == 2

    def test_nested_path(self):
        raw = """
=== FILE: src/routes/auth.py ===
def login():
    pass
"""
        files = parse_generated_files(raw)
        assert "src/routes/auth.py" in files

    def test_strips_markdown_fences(self):
        raw = """
=== FILE: app.py ===
```python
print("hello")
```
"""
        files = parse_generated_files(raw)
        assert "```" not in files["app.py"]
        assert 'print("hello")' in files["app.py"]

    def test_empty_input_returns_empty_dict(self):
        files = parse_generated_files("")
        assert files == {}

    def test_no_file_markers_returns_empty_dict(self):
        files = parse_generated_files("Here is some code without markers")
        assert files == {}

    def test_preserves_content(self):
        content = "line1\nline2\nline3"
        raw = f"=== FILE: test.py ===\n{content}"
        files = parse_generated_files(raw)
        assert files["test.py"] == content

    def test_readme_file(self):
        raw = """
=== FILE: README.md ===
# My Project

This is a secure app.
"""
        files = parse_generated_files(raw)
        assert "README.md" in files
        assert "# My Project" in files["README.md"]


# ------------------------------------------------------------------
# run_pipeline() with mocked Groq
# ------------------------------------------------------------------

MOCK_GROQ_RESPONSE = """
=== FILE: app.py ===
from flask import Flask
app = Flask(__name__)

=== FILE: requirements.txt ===
flask>=2.0
python-dotenv>=1.0

=== FILE: README.md ===
# Secure Flask App
"""

class TestRunPipeline:

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_returns_dict(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask login API",
            output_dir=str(tmp_path)
        )
        assert isinstance(result, dict)

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_has_all_keys(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask login API",
            output_dir=str(tmp_path)
        )
        expected_keys = {
            "owasp_domains", "mitre_threats",
            "security_context", "raw_output",
            "files", "saved_paths"
        }
        assert expected_keys.issubset(result.keys())

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_saves_files(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask login API",
            output_dir=str(tmp_path)
        )
        assert len(result["saved_paths"]) == 3
        for path in result["saved_paths"]:
            assert os.path.exists(path)

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_detects_owasp_domains(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask JWT login API with database",
            output_dir=str(tmp_path)
        )
        assert len(result["owasp_domains"]) > 0
        assert "authentication" in result["owasp_domains"]

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_detects_mitre_threats_for_llm(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a chatbot with LLM integration and login",
            output_dir=str(tmp_path)
        )
        assert "Prompt Injection" in result["mitre_threats"]

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_pipeline_files_written_correctly(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask API",
            output_dir=str(tmp_path)
        )
        app_path = tmp_path / "app.py"
        assert app_path.exists()
        content = app_path.read_text(encoding="utf-8")
        assert "Flask" in content

    @patch("src.pipeline.generate_code", return_value="No file markers here")
    def test_pipeline_fallback_on_no_file_markers(self, mock_generate, tmp_path):
        """If LLM returns output without === FILE: === markers, save as single file."""
        result = run_pipeline(
            "Build something",
            output_dir=str(tmp_path)
        )
        assert "generated_code.txt" in result["files"]

    @patch("src.pipeline.generate_code", return_value=MOCK_GROQ_RESPONSE)
    def test_security_context_in_result(self, mock_generate, tmp_path):
        result = run_pipeline(
            "Build a Flask JWT login API",
            output_dir=str(tmp_path)
        )
        assert "OWASP" in result["security_context"]
