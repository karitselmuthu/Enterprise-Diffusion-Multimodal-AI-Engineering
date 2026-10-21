from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    length: int = Field(default=8, ge=1, le=64)
    steps: int = Field(default=4, ge=1, le=64)
    prefix: list[str] = Field(default_factory=list)
    seed: int = 7


class MaskRequest(BaseModel):
    tokens: list[str] = Field(min_length=1, max_length=128)
    probability: float = Field(default=0.4, ge=0, le=1)
    seed: int = 7
