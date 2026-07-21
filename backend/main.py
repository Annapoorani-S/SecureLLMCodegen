"""FastAPI application for the AISAF secure code-generation pipeline."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.pipeline import build_combined_context, run_pipeline


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

app = FastAPI(
    title="AISAF API",
    version="1.0.0",
    description="Security-aware AI code generation using OWASP and MITRE ATLAS guidance.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class RequirementRequest(BaseModel):
    requirement: str = Field(min_length=3, max_length=10_000)


class AnalysisResponse(BaseModel):
    owasp_domains: list[str]
    mitre_threats: list[str]
    security_context: str


class GenerationResponse(AnalysisResponse):
    files: dict[str, str]
    saved_paths: list[str]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aisaf-api"}


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_requirement(payload: RequirementRequest) -> AnalysisResponse:
    context, owasp_domains, mitre_threats = build_combined_context(payload.requirement)
    return AnalysisResponse(
        owasp_domains=owasp_domains,
        mitre_threats=mitre_threats,
        security_context=context,
    )


@app.post("/api/generate", response_model=GenerationResponse)
def generate_project(payload: RequirementRequest) -> GenerationResponse:
    request_output_dir = OUTPUT_DIR / uuid.uuid4().hex
    try:
        result = run_pipeline(payload.requirement, output_dir=str(request_output_dir))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Code generation failed.") from exc

    return GenerationResponse(
        owasp_domains=result["owasp_domains"],
        mitre_threats=result["mitre_threats"],
        security_context=result["security_context"],
        files=result["files"],
        saved_paths=result["saved_paths"],
    )
