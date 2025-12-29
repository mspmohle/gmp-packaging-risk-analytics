#============================================================
# main.py — FastAPI app for GMP Packaging Risk Analytics
#
# Goal:
#   Serve local dashboard exports (from EXPORTS.json) via a lightweight API.
#
# Notes:
#   - data/processed/** is gitignored; endpoints expect local files present.
#   - EXPORTS.json is the authoritative index written by notebooks/scripts.
#   - EXPORTS.json currently uses STRING paths (export_dir/published_dir/pointer/files.*).
#   - Filenames inside "files" may contain dots (e.g., *.json, *.csv).
#============================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse


# --- Paths --------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # .../gmp-packaging-risk-analytics
EXPORTS_INDEX_PATH = REPO_ROOT / "EXPORTS.json"

app = FastAPI(title="GMP Packaging Risk Analytics API", version="0.1.0")


# --- Helpers ------------------------------------------------------------------
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_exports_index() -> Dict[str, Any]:
    if not EXPORTS_INDEX_PATH.exists():
        raise HTTPException(status_code=404, detail=f"EXPORTS.json not found at {EXPORTS_INDEX_PATH}")
    try:
        return json.loads(EXPORTS_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"EXPORTS.json invalid JSON: {e}")


def normalize_path(p_str: str) -> Path:
    p = Path(p_str)
    if p.is_absolute():
        return p
    return (REPO_ROOT / p_str).resolve()


def get_nested(d: Dict[str, Any], dotted: str) -> Any:
    """
    Dotted traversal with a special-case for `.files.<filename-with-dots>`.

    Example key:
      risk_scoring.latest_test.files.dashboard_kpis_test.json

    Resolves to:
      d["risk_scoring"]["latest_test"]["files"]["dashboard_kpis_test.json"]
    """
    parts = dotted.split(".")
    cur: Any = d
    i = 0

    while i < len(parts):
        if not isinstance(cur, dict):
            raise HTTPException(status_code=404, detail=f"Key not found: {dotted}")

        part = parts[i]

        # Special handling: after "files", remainder is the literal filename
        if part == "files":
            if "files" not in cur or not isinstance(cur["files"], dict):
                raise HTTPException(status_code=404, detail=f"Key not found: {dotted}")
            cur = cur["files"]

            filename = ".".join(parts[i + 1 :])
            if not filename:
                return cur
            if filename not in cur:
                raise HTTPException(status_code=404, detail=f"Key not found: {dotted}")
            return cur[filename]

        if part not in cur:
            raise HTTPException(status_code=404, detail=f"Key not found: {dotted}")

        cur = cur[part]
        i += 1

    return cur


def resolve_path_obj(obj: Any) -> Path:
    """
    Resolve obj to a Path. Supports:
      - string path
      - dict with string pointer/published_dir/export_dir
    """
    if isinstance(obj, str):
        return normalize_path(obj)

    if isinstance(obj, dict):
        for candidate in ("pointer", "published_dir", "export_dir"):
            if candidate in obj and isinstance(obj[candidate], str):
                return normalize_path(obj[candidate])

    raise HTTPException(
        status_code=400,
        detail="Key does not resolve to a path (expected string path or dict with pointer/published_dir/export_dir).",
    )


def path_stats(p: Path) -> Dict[str, Any]:
    return {
        "path": str(p),
        "exists": p.exists(),
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "size_bytes": (p.stat().st_size if p.exists() and p.is_file() else None),
    }


# --- Routes -------------------------------------------------------------------
@app.get("/", tags=["meta"])
def root() -> Dict[str, Any]:
    return {
        "name": "GMP Packaging Risk Analytics API",
        "version": app.version,
        "repo_root": str(REPO_ROOT),
        "exports_index_path": str(EXPORTS_INDEX_PATH),
        "utc_now": utc_now_iso(),
    }


@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/db/info", tags=["db"])
def db_info() -> Dict[str, Any]:
    return {
        "db_enabled": False,
        "message": "DB not used. Use /exports/* endpoints.",
        "utc_now": utc_now_iso(),
    }


@app.get("/exports/index", tags=["exports"])
def exports_index() -> Dict[str, Any]:
    return load_exports_index()


@app.get("/exports/resolve", tags=["exports"])
def exports_resolve(
    key: str = Query(..., description="Dotted key into EXPORTS.json, e.g. risk_scoring.latest_test"),
) -> Dict[str, Any]:
    idx = load_exports_index()
    obj = get_nested(idx, key)
    p = resolve_path_obj(obj)

    out = {"key": key, "utc_now": utc_now_iso()}
    out.update(path_stats(p))
    return out


@app.get("/exports/file", tags=["exports"])
def exports_file(
    key: str = Query(..., description="Dotted key that resolves to a file path"),
    as_text: bool = Query(True, description="Return csv/txt/md as text/plain (instead of download)"),
) -> Any:
    idx = load_exports_index()
    obj = get_nested(idx, key)
    p = resolve_path_obj(obj)

    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Resolved path does not exist: {p}")
    if p.is_dir():
        raise HTTPException(status_code=400, detail=f"Resolved path is a directory: {p}")

    suffix = p.suffix.lower()

    if suffix == ".json":
        return json.loads(p.read_text(encoding="utf-8"))

    if suffix in (".csv", ".txt", ".log", ".md"):
        if as_text:
            return PlainTextResponse(p.read_text(encoding="utf-8", errors="replace"))
        return FileResponse(str(p))

    return FileResponse(str(p))
