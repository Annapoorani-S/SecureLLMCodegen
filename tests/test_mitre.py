"""
tests/test_mitre.py

Unit tests for the MITRE ATLAS Context Engine.
No Groq API key required - tests are purely local.
"""

import pytest
from src.mitre_atlas import MITRE_ATTACKS
from src.mitre_context import detect_ai_threats, build_mitre_context


# ------------------------------------------------------------------
# Knowledge Base Integrity Tests
# ------------------------------------------------------------------

class TestMitreAtlasKnowledgeBase:

    def test_knowledge_base_is_list(self):
        assert isinstance(MITRE_ATTACKS, list)

    def test_knowledge_base_not_empty(self):
        assert len(MITRE_ATTACKS) > 0

    def test_each_entry_has_required_fields(self):
        required = {"id", "name", "tactic", "keywords", "mitigation"}
        for attack in MITRE_ATTACKS:
            missing = required - attack.keys()
            assert not missing, f"Entry {attack.get('id')} missing fields: {missing}"

    def test_keywords_are_lists(self):
        for attack in MITRE_ATTACKS:
            assert isinstance(attack["keywords"], list), \
                f"Entry {attack['id']}: keywords must be a list"

    def test_mitigations_are_lists(self):
        for attack in MITRE_ATTACKS:
            assert isinstance(attack["mitigation"], list), \
                f"Entry {attack['id']}: mitigation must be a list"

    def test_no_empty_mitigations(self):
        for attack in MITRE_ATTACKS:
            assert len(attack["mitigation"]) > 0, \
                f"Entry {attack['id']} has no mitigations"

    def test_covers_prompt_injection(self):
        ids = [a["id"] for a in MITRE_ATTACKS]
        names = [a["name"] for a in MITRE_ATTACKS]
        assert any("Prompt Injection" in n for n in names), \
            "Knowledge base should include Prompt Injection"

    def test_covers_data_poisoning(self):
        names = [a["name"] for a in MITRE_ATTACKS]
        assert any("Poisoning" in n for n in names)

    def test_covers_model_theft(self):
        names = [a["name"] for a in MITRE_ATTACKS]
        assert any("Theft" in n or "Extraction" in n for n in names)


# ------------------------------------------------------------------
# detect_ai_threats() tests
# ------------------------------------------------------------------

class TestDetectAiThreats:

    def test_chatbot_triggers_prompt_injection(self):
        threats = detect_ai_threats("Build a chatbot using an LLM")
        assert "Prompt Injection" in threats

    def test_login_triggers_brute_force(self):
        threats = detect_ai_threats("Build a login system")
        assert "Brute Force" in threats

    def test_training_triggers_data_poisoning(self):
        threats = detect_ai_threats("Fine-tune a model on training data")
        assert "Data Poisoning" in threats

    def test_api_triggers_exploit(self):
        threats = detect_ai_threats("Build a REST API with FastAPI")
        assert "Exploit Public-Facing Application" in threats

    def test_no_threats_returns_empty(self):
        # A very plain requirement with no AI/security keywords
        threats = detect_ai_threats("print hello world")
        # Should return an empty list (no matches)
        assert isinstance(threats, list)

    def test_returns_list(self):
        threats = detect_ai_threats("Build a chatbot with login")
        assert isinstance(threats, list)

    def test_case_insensitive(self):
        threats = detect_ai_threats("BUILD A CHATBOT")
        assert "Prompt Injection" in threats

    def test_no_duplicates(self):
        threats = detect_ai_threats(
            "Build a chatbot LLM assistant with prompt and chat"
        )
        assert len(threats) == len(set(threats)), "Detected threats should not contain duplicates"

    def test_agent_triggers_tool_abuse(self):
        threats = detect_ai_threats("Build an AI agent with tool use and function calling")
        assert "LLM Plugin / Tool Abuse" in threats

    def test_ml_model_triggers_model_theft(self):
        threats = detect_ai_threats("Expose an ML model inference API endpoint")
        assert "Model Theft / Extraction" in threats


# ------------------------------------------------------------------
# build_mitre_context() tests
# ------------------------------------------------------------------

class TestBuildMitreContext:

    def test_returns_string(self):
        ctx = build_mitre_context("Build a chatbot")
        assert isinstance(ctx, str)

    def test_chatbot_context_not_empty(self):
        ctx = build_mitre_context("Build a chatbot using LLM")
        assert len(ctx) > 0

    def test_contains_mitre_reference(self):
        ctx = build_mitre_context("Build a chatbot")
        assert "MITRE ATLAS" in ctx

    def test_contains_technique_id(self):
        ctx = build_mitre_context("Build a chatbot")
        # Prompt Injection technique ID
        assert "AML.T0051" in ctx

    def test_contains_bullet_mitigations(self):
        ctx = build_mitre_context("Build a chatbot")
        assert "- " in ctx

    def test_no_match_returns_empty_string(self):
        ctx = build_mitre_context("print hello world")
        assert ctx == ""

    def test_multiple_threats_in_context(self):
        ctx = build_mitre_context(
            "Build a chatbot with login authentication for an ML model API"
        )
        # Should include both prompt injection and brute force mitigations
        assert "Prompt Injection" in ctx
        assert "Brute Force" in ctx

    def test_context_has_header(self):
        ctx = build_mitre_context("Build a chatbot with LLM")
        assert "MITRE ATLAS" in ctx
        assert "AI/ML Threat" in ctx
