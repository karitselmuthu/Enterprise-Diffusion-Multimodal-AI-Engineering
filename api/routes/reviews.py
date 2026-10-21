"""Authenticated review queue for human verification of generated findings."""

from __future__ import annotations

import os
import json
from pathlib import Path
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException

from api.routes.multimodal import decode_payload
from api.schemas.review import ReviewCreate, ReviewDecision
from src.multimodal.incident_analyzer import analyze_incident
from src.review.store import ReviewStore

router = APIRouter(prefix="/reviews", tags=["human review"])


def require_review_key(x_review_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get("REVIEW_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Set REVIEW_API_KEY to enable review endpoints")
    if not x_review_key or not secrets.compare_digest(x_review_key, expected):
        raise HTTPException(status_code=401, detail="Invalid review key")


def store() -> ReviewStore:
    return ReviewStore(Path(os.environ.get("REVIEW_DB_PATH", "data/reviews.sqlite3")))


def reviewer_identity(x_reviewer_key: str | None = Header(default=None)) -> str:
    raw = os.environ.get("REVIEWER_KEYS_JSON")
    if not raw:
        raise HTTPException(status_code=503, detail="Set REVIEWER_KEYS_JSON to enable decisions")
    try:
        keys = json.loads(raw)
        if not isinstance(keys, dict) or not keys or any(not isinstance(name, str) or not isinstance(key, str) or not key for name, key in keys.items()):
            raise ValueError("invalid reviewer keys")
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=503, detail="Invalid REVIEWER_KEYS_JSON") from exc
    for name, key in keys.items():
        if x_reviewer_key and secrets.compare_digest(x_reviewer_key, key):
            return name
    raise HTTPException(status_code=401, detail="Invalid reviewer key")


@router.post("", dependencies=[Depends(require_review_key)], status_code=201)
def create_review(request: ReviewCreate) -> dict:
    try:
        analysis = analyze_incident(text=request.text, image_bytes=decode_payload(request.image_base64),
                                    document_bytes=decode_payload(request.document_base64),
                                    document_name=request.document_name, backend=request.backend)
        return store().create(analysis)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", dependencies=[Depends(require_review_key)])
def list_reviews(status: str = "pending", limit: int = 50) -> list[dict]:
    try:
        return store().list(status=status, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{identifier}", dependencies=[Depends(require_review_key)])
def get_review(identifier: str) -> dict:
    record = store().get(identifier)
    if record is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return record


@router.post("/{identifier}/decision", dependencies=[Depends(require_review_key)])
def decide_review(identifier: str, request: ReviewDecision, identity: str = Depends(reviewer_identity)) -> dict:
    if request.reviewer != identity:
        raise HTTPException(status_code=403, detail="Reviewer identity does not match key")
    try:
        return store().decide(identifier, **request.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Review not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
