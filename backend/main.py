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
REPORTS_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

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
# Generate Project
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
        )

# ==========================================================
# Output Directory Tree
# ==========================================================

def _build_tree(path: Path, base: Path) -> dict:
    """Recursively build a tree node for the given path."""
    rel = path.relative_to(base)
    node = {
        "name": path.name,
        "path": rel.as_posix(),
        "type": "directory" if path.is_dir() else "file",
    }
    if path.is_dir():
        children = []
        for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            children.append(_build_tree(child, base))
        node["children"] = children
    return node


@app.get("/api/output/tree")
def output_tree():
    """Return the recursive directory tree of the output folder."""
    if not OUTPUT_DIR.exists() or not any(OUTPUT_DIR.iterdir()):
        return {"name": "output", "path": "", "type": "directory", "children": []}
    return _build_tree(OUTPUT_DIR, OUTPUT_DIR)


@app.get("/api/output/file")
def output_file(path: str):
    """Return the raw content of a file inside the output folder."""
    # Sanitize: prevent path traversal
    safe_path = OUTPUT_DIR / path
    try:
        safe_path = safe_path.resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path.")

    if not str(safe_path).startswith(str(OUTPUT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        content = safe_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"path": path, "content": content}


# ==========================================================
# Reports Directory
# ==========================================================

@app.get("/api/reports/list")
def reports_list():
    """Return a list of available reports."""
    if not REPORTS_DIR.exists():
        return []
    
    reports = []
    for f in REPORTS_DIR.iterdir():
        if f.is_file() and f.suffix in [".json", ".html", ".md"]:
            reports.append({
                "name": f.name,
                "path": f.name,
                "type": "file"
            })
    return sorted(reports, key=lambda x: x["name"])


@app.get("/api/reports/file")
def reports_file(filename: str):
    """Return the raw content of a report."""
    safe_path = REPORTS_DIR / filename
    try:
        safe_path = safe_path.resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path.")

    if not str(safe_path).startswith(str(REPORTS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        content = safe_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"path": filename, "content": content}

# ==========================================================
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