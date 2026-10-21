from pydantic import BaseModel, Field

from api.schemas.multimodal import IncidentRequest


class ReviewCreate(IncidentRequest):
    pass


class ReviewDecision(BaseModel):
    status: str
    reviewer: str = Field(min_length=1, max_length=100)
    summary: str = Field(min_length=1, max_length=2000)
    recommendation: str = Field(default="", max_length=2000)
    cited_sources: list[str] = Field(default_factory=list, max_length=20)
