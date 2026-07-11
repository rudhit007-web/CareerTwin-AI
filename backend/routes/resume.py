"""
CareerTwin AI – Resume Routes
POST /api/resume/upload     – upload and extract text
POST /api/resume/analyze    – run Granite analysis on latest resume
GET  /api/resume            – get latest analysis result
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import (
    create_document, get_latest_resume_analysis,
    create_resume_analysis, get_user_documents,
)
from database.models import User, DocumentType, AnalysisStatus
from utils.auth import get_current_user
from services.storage_service import save_upload_file
from services.document_service import extract_text
from services.ai_service import analyze_resume

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_path = await save_upload_file(file)
    extracted = extract_text(file_path, file.content_type)

    doc = await create_document(
        db=db,
        user_id=current_user.id,
        document_type=DocumentType.RESUME,
        original_filename=file.filename,
        file_path=file_path,
        file_size_bytes=len(extracted.encode()),
        content_type=file.content_type,
        extracted_text=extracted,
    )
    return {
        "document_id": doc.id,
        "filename": doc.original_filename,
        "extracted_chars": len(extracted),
        "status": "uploaded",
    }


@router.post("/analyze")
async def analyze_latest_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    docs = await get_user_documents(db, current_user.id)
    resume_docs = [d for d in docs if d.document_type == DocumentType.RESUME and d.extracted_text]
    if not resume_docs:
        raise HTTPException(status_code=404, detail="No uploaded resume found. Please upload a resume first.")

    latest_doc = resume_docs[0]
    result = await analyze_resume(latest_doc.extracted_text)
    tokens = result.pop("tokens_used", 0)

    analysis = await create_resume_analysis(
        db=db,
        user_id=current_user.id,
        document_id=latest_doc.id,
        result=result,
        tokens_used=tokens,
    )
    return {
        "analysis_id": analysis.id,
        "summary": analysis.summary,
        "ats_score": analysis.ats_score,
        "skills_found": analysis.skills_found or [],
        "missing_skills": analysis.missing_skills or [],
        "suggestions": analysis.suggestions or [],
        "career_suggestions": analysis.career_suggestions or [],
    }


@router.get("")
async def get_resume_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_latest_resume_analysis(db, current_user.id)
    if not analysis:
        return {}
    return {
        "analysis_id": analysis.id,
        "summary": analysis.summary,
        "ats_score": analysis.ats_score,
        "skills_found": analysis.skills_found or [],
        "missing_skills": analysis.missing_skills or [],
        "suggestions": analysis.suggestions or [],
        "career_suggestions": analysis.career_suggestions or [],
    }
