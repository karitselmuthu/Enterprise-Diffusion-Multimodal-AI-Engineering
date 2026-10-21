import random

from fastapi import APIRouter, HTTPException

from api.schemas.diffusion import GenerateRequest, MaskRequest
from src.diffusion.generator import BigramBaseline, generate
from src.diffusion.masking import mask_tokens
from src.evaluation.runner import benchmark, train_default

router = APIRouter(prefix="/diffusion", tags=["diffusion"])
_model = None
_baseline = None


def models():
    global _model, _baseline
    if _model is None:
        _model, train, _, _ = train_default()
        _baseline = BigramBaseline(train)
    return _model, _baseline


@router.post("/mask")
def mask(request: MaskRequest) -> dict:
    tokens, positions = mask_tokens(request.tokens, request.probability, random.Random(request.seed))
    return {"tokens": tokens, "masked_positions": positions}


@router.post("/generate")
def generate_text(request: GenerateRequest) -> dict:
    model, _ = models()
    try:
        return generate(model, **request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/baseline")
def generate_baseline(request: GenerateRequest) -> dict:
    _, baseline = models()
    try:
        return baseline.generate(request.length, prefix=request.prefix, seed=request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/benchmark")
def diffusion_benchmark(steps: int = 4, epochs: int = 20) -> dict:
    if not 1 <= steps <= 64 or not 1 <= epochs <= 100:
        raise HTTPException(status_code=422, detail="steps must be 1..64 and epochs 1..100")
    return benchmark(steps=steps, epochs=epochs)
