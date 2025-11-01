from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.document import DocumentResponse


class ProjectCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=200, example="My Project"
    )
    description: Optional[str] = Field(
        None, max_length=500, example="Project description"
    )


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=200, example="Updated Project Name"
    )
    description: Optional[str] = Field(
        None, max_length=500, example="Updated description"
    )


class ProjectResponse(BaseModel):
    id: int = Field(..., ge=1, example=1)
    name: str = Field(
        ..., min_length=1, max_length=200, example="My Project"
    )
    description: Optional[str] = Field(
        None, max_length=500, example="Project description"
    )
    owner_id: int = Field(..., ge=1, example=42)
    created_at: datetime = Field(..., example="2025-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-01-02T12:00:00Z")
    documents: List[DocumentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int = Field(..., ge=1, example=1)
    name: str = Field(
        ..., min_length=1, max_length=200, example="My Project"
    )
    description: Optional[str] = Field(
        None, max_length=500, example="Project description"
    )
    owner_id: int = Field(..., ge=1, example=42)
    created_at: datetime = Field(..., example="2025-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-01-02T12:00:00Z")
    documents: List[DocumentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
