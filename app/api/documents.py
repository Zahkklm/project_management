import io
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_project_role
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.s3_service_refactored import S3Service

s3_service = S3Service()

# Error message constants
DOCUMENT_NOT_FOUND = "Document not found"

s3_service = S3Service()

router = APIRouter()


@router.get(
    "/project/{project_id}/documents", response_model=List[DocumentResponse]
)
def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user)
    documents = (
        db.query(Document).filter(Document.project_id == project_id).all()
    )
    return documents


@router.post(
    "/project/{project_id}/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    project_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_role(project_id, db, current_user)
    uploaded_documents = []
    for file in files:
        content = await file.read()
        s3_key = s3_service.upload_file(
            content, str(file.filename or ""), str(file.content_type or "")
        )
        if not s3_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(f"Failed to upload {file.filename}"),
            )
        document = Document(
            filename=str(file.filename),
            s3_key=str(s3_key),
            content_type=str(file.content_type),
            size=int(len(content)),
            project_id=int(project_id),
        )
        db.add(document)
        uploaded_documents.append(document)
    db.commit()
    for doc in uploaded_documents:
        db.refresh(doc)
    return uploaded_documents


@router.get("/document/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOCUMENT_NOT_FOUND,
        )
    require_project_role(int(document.project_id), db, current_user)
    from app.core.config import settings

    file_content = s3_service.download_file(
        settings.S3_BUCKET_NAME, str(document.s3_key)
    )
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document",
        )
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=str(document.content_type),
        headers={
            "Content-Disposition": (
                f"attachment; filename={str(document.filename)}"
            )
        },
    )


@router.put("/document/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOCUMENT_NOT_FOUND,
        )
    require_project_role(int(document.project_id), db, current_user)
    from app.core.config import settings

    s3_service.delete_file(settings.S3_BUCKET_NAME, str(document.s3_key))
    content = await file.read()
    s3_key = s3_service.upload_file(
        content, str(file.filename or ""), str(file.content_type or "")
    )
    if not s3_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )
    setattr(document, "filename", str(file.filename))
    setattr(document, "s3_key", str(s3_key))
    setattr(document, "content_type", str(file.content_type))
    setattr(document, "size", int(len(content)))
    db.commit()
    db.refresh(document)
    return document


@router.delete(
    "/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DOCUMENT_NOT_FOUND,
        )
    require_project_role(int(document.project_id), db, current_user)
    from app.core.config import settings

    s3_service.delete_file(settings.S3_BUCKET_NAME, str(document.s3_key))
    db.delete(document)
    db.commit()
