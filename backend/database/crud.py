"""
CareerTwin AI – CRUD Operations
Reusable async database operations for all models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (
    User, UserProfile, Document, ResumeAnalysis,
    SkillGapAnalysis, CareerRoadmap, ProjectRecommendation,
    ChatSession, ChatMessage, WeeklyGoal,
    AnalysisStatus, DocumentType, MessageRole,
)


# ── Users ──────────────────────────────────────────────────────

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.profile))
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, full_name: str, hashed_password: str) -> User:
    user = User(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    # auto-create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.flush()
    return user


# ── User Profile ───────────────────────────────────────────────

async def get_profile(db: AsyncSession, user_id: str) -> Optional[UserProfile]:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def upsert_profile(db: AsyncSession, user_id: str, data: dict) -> UserProfile:
    profile = await get_profile(db, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id, **data)
        db.add(profile)
    else:
        for key, value in data.items():
            setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
    await db.flush()
    return profile


async def calculate_profile_completeness(profile: UserProfile) -> float:
    """Return a 0–100 completeness score based on filled fields."""
    fields = [
        profile.branch, profile.semester, profile.cgpa,
        profile.headline, profile.bio, profile.location,
        profile.career_goals, profile.skills, profile.education,
        profile.target_roles,
    ]
    filled = sum(1 for f in fields if f is not None and f != [] and f != "")
    return round((filled / len(fields)) * 100, 1)


# ── Documents ──────────────────────────────────────────────────

async def create_document(
    db: AsyncSession,
    user_id: str,
    document_type: DocumentType,
    original_filename: str,
    file_path: str,
    file_size_bytes: int,
    content_type: str,
    extracted_text: Optional[str] = None,
) -> Document:
    doc = Document(
        user_id=user_id,
        document_type=document_type,
        original_filename=original_filename,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        content_type=content_type,
        extracted_text=extracted_text,
        analysis_status=AnalysisStatus.PENDING,
    )
    db.add(doc)
    await db.flush()
    return doc


async def get_user_documents(db: AsyncSession, user_id: str) -> List[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.uploaded_at.desc())
    )
    return list(result.scalars().all())


async def get_document_by_id(db: AsyncSession, doc_id: str, user_id: str) -> Optional[Document]:
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user_id)
    )
    return result.scalar_one_or_none()


# ── Resume Analysis ────────────────────────────────────────────

async def create_resume_analysis(db: AsyncSession, user_id: str, document_id: str, result: dict, tokens_used: int) -> ResumeAnalysis:
    analysis = ResumeAnalysis(
        user_id=user_id,
        document_id=document_id,
        summary=result.get("summary"),
        ats_score=result.get("ats_score"),
        skills_found=result.get("skills_found", []),
        missing_skills=result.get("missing_skills", []),
        suggestions=result.get("suggestions", []),
        career_suggestions=result.get("career_suggestions", []),
        raw_result=result,
        tokens_used=tokens_used,
        status=AnalysisStatus.COMPLETED,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def get_latest_resume_analysis(db: AsyncSession, user_id: str) -> Optional[ResumeAnalysis]:
    result = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.user_id == user_id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── Skill Gap Analysis ─────────────────────────────────────────

async def create_skill_gap_analysis(db: AsyncSession, user_id: str, career_goal: str, result: dict, tokens_used: int) -> SkillGapAnalysis:
    analysis = SkillGapAnalysis(
        user_id=user_id,
        career_goal=career_goal,
        current_skills=result.get("current_skills", []),
        missing_skills=result.get("missing_skills", []),
        priority_order=result.get("priority_order", []),
        learning_roadmap=result.get("learning_roadmap", []),
        ibm_courses=result.get("ibm_courses", []),
        weekly_plan=result.get("weekly_plan", []),
        timeline_weeks=result.get("timeline_weeks"),
        tokens_used=tokens_used,
        status=AnalysisStatus.COMPLETED,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def get_latest_skill_gap(db: AsyncSession, user_id: str) -> Optional[SkillGapAnalysis]:
    result = await db.execute(
        select(SkillGapAnalysis)
        .where(SkillGapAnalysis.user_id == user_id)
        .order_by(SkillGapAnalysis.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── Career Roadmap ─────────────────────────────────────────────

async def create_career_roadmap(db: AsyncSession, user_id: str, result: dict, tokens_used: int) -> CareerRoadmap:
    roadmap = CareerRoadmap(
        user_id=user_id,
        current_position=result.get("current_position"),
        target_position=result.get("target_position"),
        required_skills=result.get("required_skills", []),
        monthly_goals=result.get("monthly_goals", []),
        ibm_certifications=result.get("ibm_certifications", []),
        expected_salary=result.get("expected_salary"),
        timeline_months=result.get("timeline_months"),
        future_scope=result.get("future_scope"),
        raw_result=result,
        tokens_used=tokens_used,
        status=AnalysisStatus.COMPLETED,
    )
    db.add(roadmap)
    await db.flush()
    return roadmap


async def get_latest_roadmap(db: AsyncSession, user_id: str) -> Optional[CareerRoadmap]:
    result = await db.execute(
        select(CareerRoadmap)
        .where(CareerRoadmap.user_id == user_id)
        .order_by(CareerRoadmap.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── Project Recommendations ────────────────────────────────────

async def create_project_recommendations(db: AsyncSession, user_id: str, projects: list, tokens_used: int) -> List[ProjectRecommendation]:
    recs = []
    for p in projects:
        rec = ProjectRecommendation(
            user_id=user_id,
            title=p.get("title", "Untitled Project"),
            problem_statement=p.get("problem_statement"),
            tech_stack=p.get("tech_stack", []),
            ibm_technologies=p.get("ibm_technologies", []),
            architecture=p.get("architecture"),
            difficulty=p.get("difficulty"),
            timeline_weeks=p.get("timeline_weeks"),
            github_structure=p.get("github_structure", []),
            learning_outcomes=p.get("learning_outcomes", []),
            tokens_used=tokens_used // max(len(projects), 1),
        )
        db.add(rec)
        recs.append(rec)
    await db.flush()
    return recs


async def get_user_projects(db: AsyncSession, user_id: str) -> List[ProjectRecommendation]:
    result = await db.execute(
        select(ProjectRecommendation)
        .where(ProjectRecommendation.user_id == user_id)
        .order_by(ProjectRecommendation.created_at.desc())
    )
    return list(result.scalars().all())


# ── Chat ───────────────────────────────────────────────────────

async def create_chat_session(db: AsyncSession, user_id: str, title: str = "New Conversation", context_type: str = "general") -> ChatSession:
    session = ChatSession(user_id=user_id, title=title, context_type=context_type)
    db.add(session)
    await db.flush()
    return session


async def get_chat_sessions(db: AsyncSession, user_id: str) -> List[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id, ChatSession.is_active == True)
        .order_by(ChatSession.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_chat_session_with_messages(db: AsyncSession, session_id: str, user_id: str) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def add_chat_message(db: AsyncSession, session_id: str, role: MessageRole, content: str, tokens_used: int = 0) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content, tokens_used=tokens_used)
    db.add(msg)
    # update session timestamp
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(updated_at=datetime.utcnow())
    )
    await db.flush()
    return msg


# ── Weekly Goals ───────────────────────────────────────────────

async def get_or_create_weekly_goal(db: AsyncSession, user_id: str, week_number: int, year: int) -> WeeklyGoal:
    result = await db.execute(
        select(WeeklyGoal)
        .where(WeeklyGoal.user_id == user_id, WeeklyGoal.week_number == week_number, WeeklyGoal.year == year)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        goal = WeeklyGoal(user_id=user_id, week_number=week_number, year=year, goals=[], completed=[])
        db.add(goal)
        await db.flush()
    return goal
