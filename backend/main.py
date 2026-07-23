"""
FastAPI application for the AISAF Secure Code Generation Pipeline
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.pipeline import (
    build_combined_context,
    run_pipeline,
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="AISAF API",
    version="1.0.0",
    description="AI Secure Architecture Framework",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Models
# ==========================================================

class RequirementRequest(BaseModel):
    requirement: str = Field(
        min_length=3,
        max_length=10000
    )


class AnalysisResponse(BaseModel):
    owasp_domains: list[str]
    mitre_threats: list[str]
    security_context: str


class GenerationResponse(BaseModel):
    owasp_domains: list[str]
    mitre_threats: list[str]
    security_context: str
    files: dict[str, str]
    saved_paths: list[str]

# ==========================================================
# Health
# ==========================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "AISAF Backend"
    }

# ==========================================================
# Analyze Requirement
# ==========================================================

@app.post("/api/generate")
def generate_project(payload: RequirementRequest):

    try:
        report = run_pipeline(payload.requirement)
        return report

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )# ==========================================================
# Run Locally
# ==========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )