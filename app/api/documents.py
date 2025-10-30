from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.s3_service import s3_service
from app.api.projects import check_project_access

router = APIRouter()


@router.get("/project/{project_id}/documents", response_model=List[DocumentResponse])
def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_project_access(project_id, current_user, db)
    documents = db.query(Document).filter(Document.project_id == project_id).all()
    return documents


@router.post("/project/{project_id}/documents", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    project_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_project_access(project_id, current_user, db)
    
    uploaded_documents = []
    for file in files:
        content = await file.read()
        s3_key = s3_service.upload_file(content, file.filename, file.content_type)
        
        if not s3_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}"
            )
        
        document = Document(
            filename=file.filename,
            s3_key=s3_key,
            content_type=file.content_type,
            size=len(content),
            project_id=project_id
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
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    check_project_access(document.project_id, current_user, db)
    
    file_content = s3_service.download_file(document.s3_key)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document"
        )
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=document.content_type,
        headers={"Content-Disposition": f"attachment; filename={document.filename}"}
    )


@router.put("/document/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    check_project_access(document.project_id, current_user, db)
    
    s3_service.delete_file(document.s3_key)
    
    content = await file.read()
    s3_key = s3_service.upload_file(content, file.filename, file.content_type)
    
    if not s3_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )
    
    document.filename = file.filename
    document.s3_key = s3_key
    document.content_type = file.content_type
    document.size = len(content)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    check_project_access(document.project_id, current_user, db)
    
    s3_service.delete_file(document.s3_key)
    db.delete(document)
    db.commit()
