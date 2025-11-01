from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int = Field(..., ge=1, example=1)
    filename: str = Field(
        ..., min_length=1, max_length=255, example="report.pdf"
    )
    content_type: Optional[str] = Field(
        None, pattern=r"^[\w\-]+/[\w\-]+$", example="application/pdf"
    )
    size: Optional[int] = Field(None, ge=0, example=1024)
    project_id: int = Field(..., ge=1, example=42)
    uploaded_at: datetime = Field(..., example="2025-01-01T12:00:00Z")

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    filename: str = Field(
        ..., min_length=1, max_length=255, example="report.pdf"
    )
    content_type: str = Field(
        ..., pattern=r"^[\w\-]+/[\w\-]+$", example="application/pdf"
    )
