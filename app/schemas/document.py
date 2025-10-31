from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: Optional[str]
    size: Optional[int]
    project_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    filename: str
    content_type: str
