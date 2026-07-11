"""
CareerTwin AI – Career Routes
POST /api/career/skill-gap       – run skill gap analysis
GET  /api/career/skill-gap       – latest skill gap result
POST /api/career/roadmap         – generate career roadmap
GET  /api/career/roadmap         – latest roadmap
POST /api/career/projects        – recommend projects
GET  /api/career/projects        – saved project recommendations
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import (
    get_profile,
    create_skill_gap_analysis, get_latest_skill_gap,
    create_career_roadmap, get_latest_roadmap,
    create_project_recommendations, get_user_projects,
)
from database.models import User
from utils.auth import get_current_user
from services.ai_service import skill_gap_analysis, generate_career_roadmap, recommend_projects

router = APIRouter()


# ── Skill Gap ──────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    career_goal: str
    current_skills: Optional[List[str]] = None


@router.post("/skill-gap")
async def run_skill_gap(
    payload: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, current_user.id)
    skills = payload.current_skills or (profile.skills if profile else []) or []
    result = await skill_gap_analysis(payload.career_goal, skills)
    tokens = result.pop("tokens_used", 0)

    analysis = await create_skill_gap_analysis(
        db=db, user_id=current_user.id,
        career_goal=payload.career_goal,
        result=result, tokens_used=tokens,
    )
    return {
        "analysis_id": analysis.id,
        "career_goal": analysis.career_goal,
        "missing_skills": analysis.missing_skills or [],
        "missing_skills_count": len(analysis.missing_skills or []),
        "top_missing": [
            (s["skill"] if isinstance(s, dict) else s)
            for s in (analysis.missing_skills or [])[:5]
        ],
        "priority_order": analysis.priority_order or [],
        "learning_roadmap": analysis.learning_roadmap or [],
        "ibm_courses": analysis.ibm_courses or [],
        "weekly_plan": analysis.weekly_plan or [],
        "timeline_weeks": analysis.timeline_weeks,
    }


@router.get("/skill-gap")
async def get_skill_gap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_latest_skill_gap(db, current_user.id)
    if not analysis:
        return {}
    return {
        "analysis_id": analysis.id,
        "career_goal": analysis.career_goal,
        "missing_skills": analysis.missing_skills or [],
        "missing_skills_count": len(analysis.missing_skills or []),
        "top_missing": [
            (s["skill"] if isinstance(s, dict) else s)
            for s in (analysis.missing_skills or [])[:5]
        ],
        "priority_order": analysis.priority_order or [],
        "learning_roadmap": analysis.learning_roadmap or [],
        "ibm_courses": analysis.ibm_courses or [],
        "weekly_plan": analysis.weekly_plan or [],
        "timeline_weeks": analysis.timeline_weeks,
    }


# ── Career Roadmap ─────────────────────────────────────────────

@router.post("/roadmap")
async def run_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, current_user.id)
    if not profile or not profile.career_goals:
        raise HTTPException(status_code=400, detail="Please set your career goals in your profile first.")

    profile_dict = {
        "full_name": current_user.full_name,
        "branch": profile.branch,
        "semester": profile.semester,
        "cgpa": profile.cgpa,
        "career_goals": profile.career_goals,
        "skills": profile.skills or [],
    }
    result = await generate_career_roadmap(profile_dict)
    tokens = result.pop("tokens_used", 0)

    roadmap = await create_career_roadmap(db=db, user_id=current_user.id, result=result, tokens_used=tokens)
    return {
        "roadmap_id": roadmap.id,
        "current_position": roadmap.current_position,
        "target_position": roadmap.target_position,
        "required_skills": roadmap.required_skills or [],
        "monthly_goals": roadmap.monthly_goals or [],
        "ibm_certifications": roadmap.ibm_certifications or [],
        "expected_salary": roadmap.expected_salary,
        "timeline_months": roadmap.timeline_months,
        "future_scope": roadmap.future_scope,
    }


@router.get("/roadmap")
async def get_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    roadmap = await get_latest_roadmap(db, current_user.id)
    if not roadmap:
        return {}
    return {
        "roadmap_id": roadmap.id,
        "current_position": roadmap.current_position,
        "target_position": roadmap.target_position,
        "required_skills": roadmap.required_skills or [],
        "monthly_goals": roadmap.monthly_goals or [],
        "ibm_certifications": roadmap.ibm_certifications or [],
        "expected_salary": roadmap.expected_salary,
        "timeline_months": roadmap.timeline_months,
        "future_scope": roadmap.future_scope,
    }


# ── Projects ───────────────────────────────────────────────────

class ProjectsRequest(BaseModel):
    career_goal: Optional[str] = None


@router.post("/projects")
async def run_projects(
    payload: ProjectsRequest = ProjectsRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, current_user.id)
    career_goal = payload.career_goal or (profile.career_goals if profile else "") or "Software Engineer"
    skills = (profile.skills if profile else []) or []
    profile_dict = {
        "branch": profile.branch if profile else "Computer Science",
        "full_name": current_user.full_name,
    }

    result = await recommend_projects(profile_dict, skills, career_goal)
    tokens = result.pop("tokens_used", 0)
    projects_data = result.get("projects", [])

    recs = await create_project_recommendations(db=db, user_id=current_user.id, projects=projects_data, tokens_used=tokens)
    return {
        "projects": [
            {
                "id": r.id,
                "title": r.title,
                "problem_statement": r.problem_statement,
                "tech_stack": r.tech_stack or [],
                "ibm_technologies": r.ibm_technologies or [],
                "architecture": r.architecture,
                "difficulty": r.difficulty,
                "timeline_weeks": r.timeline_weeks,
                "github_structure": r.github_structure or [],
                "learning_outcomes": r.learning_outcomes or [],
            }
            for r in recs
        ]
    }


@router.get("/projects")
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recs = await get_user_projects(db, current_user.id)
    return {
        "projects": [
            {
                "id": r.id,
                "title": r.title,
                "problem_statement": r.problem_statement,
                "tech_stack": r.tech_stack or [],
                "ibm_technologies": r.ibm_technologies or [],
                "architecture": r.architecture,
                "difficulty": r.difficulty,
                "timeline_weeks": r.timeline_weeks,
                "github_structure": r.github_structure or [],
                "learning_outcomes": r.learning_outcomes or [],
            }
            for r in recs
        ]
    }
