"""
CareerTwin AI – Profile Routes
GET  /api/profile
PUT  /api/profile
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import get_profile, upsert_profile, calculate_profile_completeness
from database.models import User
from utils.auth import get_current_user

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    branch: Optional[str] = None
    semester: Optional[str] = None
    cgpa: Optional[float] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    experience_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None


@router.get("")
async def get_profile_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, current_user.id)
    if not profile:
        return {"profile": {}}
    completeness = await calculate_profile_completeness(profile)
    return {
        "profile": {
            "branch": profile.branch,
            "semester": profile.semester,
            "cgpa": profile.cgpa,
            "headline": profile.headline,
            "bio": profile.bio,
            "location": profile.location,
            "phone": profile.phone,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "experience_level": profile.experience_level,
            "career_goals": profile.career_goals,
            "skills": profile.skills or [],
            "certifications": profile.certifications or [],
            "target_roles": profile.target_roles or [],
            "target_industries": profile.target_industries or [],
            "profile_completeness": completeness,
        }
    }


@router.put("")
async def update_profile_route(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    profile = await upsert_profile(db, current_user.id, data)
    completeness = await calculate_profile_completeness(profile)
    profile.profile_completeness = completeness
    await db.flush()
    return {"profile_completeness": completeness}
