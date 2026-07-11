"""
CareerTwin AI – Documents Routes
GET    /api/documents           – list all user documents
DELETE /api/documents/{doc_id}  – delete a document
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import get_user_documents, get_document_by_id
from database.models import User
from utils.auth import get_current_user
from services.storage_service import delete_upload_file

router = APIRouter()


@router.get("")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    docs = await get_user_documents(db, current_user.id)
    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.original_filename,
                "document_type": d.document_type,
                "file_size_bytes": d.file_size_bytes,
                "content_type": d.content_type,
                "analysis_status": d.analysis_status,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in docs
        ]
    }


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await get_document_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    delete_upload_file(doc.file_path)
    await db.delete(doc)
    return {"deleted": True, "document_id": doc_id}
