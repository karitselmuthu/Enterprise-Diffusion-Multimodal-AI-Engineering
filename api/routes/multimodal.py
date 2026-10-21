"""JSON incident endpoint. Binary inputs are base64 encoded, with strict limits."""

import base64
import binascii

from fastapi import APIRouter, HTTPException

from api.schemas.multimodal import IncidentRequest
from src.multimodal.incident_analyzer import analyze_incident

router = APIRouter(prefix="/multimodal", tags=["multimodal"])


def decode_payload(value: str | None) -> bytes | None:
    if value is None:
        return None
    if len(value) > 6_700_000:
        raise ValueError("encoded input exceeds size limit")
    try:
        result = base64.b64decode(value, validate=True)
    except binascii.Error as exc:
        raise ValueError("input must be valid base64") from exc
    if len(result) > 5_000_000:
        raise ValueError("decoded input exceeds 5 MB limit")
    return result


@router.post("/analyze")
def analyze(request: IncidentRequest) -> dict:
    try:
        return analyze_incident(text=request.text, image_bytes=decode_payload(request.image_base64),
                                document_bytes=decode_payload(request.document_base64),
                                document_name=request.document_name, backend=request.backend,
                                model_path=request.model_path)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
