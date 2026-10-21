from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    text: str = Field(default="", max_length=20_000)
    image_base64: str | None = None
    document_base64: str | None = None
    document_name: str | None = None
    backend: str = "mock"
