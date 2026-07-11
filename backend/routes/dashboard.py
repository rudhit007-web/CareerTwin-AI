"""
CareerTwin AI – Dashboard Route
GET /api/dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import (
    get_profile, calculate_profile_completeness,
    get_latest_resume_analysis,
    get_latest_skill_gap,
    get_latest_roadmap,
    get_user_projects,
    get_or_create_weekly_goal,
)
from database.models import User
from utils.auth import get_current_user
from datetime import date

router = APIRouter()


@router.get("")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile     = await get_profile(db, current_user.id)
    resume      = await get_latest_resume_analysis(db, current_user.id)
    skill_gap   = await get_latest_skill_gap(db, current_user.id)
    roadmap     = await get_latest_roadmap(db, current_user.id)
    projects    = await get_user_projects(db, current_user.id)

    today = date.today()
    week_number = today.isocalendar()[1]
    weekly_goal = await get_or_create_weekly_goal(db, current_user.id, week_number, today.year)

    profile_completeness = await calculate_profile_completeness(profile) if profile else 0.0
    resume_score = resume.ats_score if resume else 0
    missing_count = len(skill_gap.missing_skills or []) if skill_gap else 0
    skill_coverage = max(0, 100 - missing_count * 10)
    career_readiness = round((profile_completeness + resume_score + skill_coverage) / 3, 1)

    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
        },
        "profile_completeness": profile_completeness,
        "career_readiness_score": career_readiness,
        "current_skills": profile.skills if profile else [],
        "resume": {
            "ats_score": resume.ats_score if resume else None,
            "skills_found": resume.skills_found if resume else [],
            "missing_skills": resume.missing_skills if resume else [],
        } if resume else None,
        "skill_gap": {
            "missing_skills_count": missing_count,
            "top_missing": [
                (s["skill"] if isinstance(s, dict) else s)
                for s in (skill_gap.missing_skills or [])[:5]
            ],
        } if skill_gap else None,
        "roadmap": {
            "current_position": roadmap.current_position,
            "target_position": roadmap.target_position,
            "timeline_months": roadmap.timeline_months,
            "expected_salary": roadmap.expected_salary,
        } if roadmap else None,
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "difficulty": p.difficulty,
                "timeline_weeks": p.timeline_weeks,
                "ibm_technologies": p.ibm_technologies or [],
            }
            for p in projects[:3]
        ],
        "weekly_goal": {
            "goals": weekly_goal.goals or [],
            "completed": weekly_goal.completed or [],
        },
    }
