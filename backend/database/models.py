"""
CareerTwin AI – SQLAlchemy ORM Models
Tables: users, user_profiles, documents, resume_analyses,
        career_roadmaps, skill_gap_analyses, project_recommendations,
        chat_sessions, chat_messages, weekly_goals
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum, Float,
    ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Enums ──────────────────────────────────────────────────────

class ExperienceLevel(str, enum.Enum):
    STUDENT   = "student"
    ENTRY     = "entry"
    MID       = "mid"
    SENIOR    = "senior"
    EXECUTIVE = "executive"


class DocumentType(str, enum.Enum):
    RESUME       = "resume"
    COVER_LETTER = "cover_letter"
    CERTIFICATE  = "certificate"
    TRANSCRIPT   = "transcript"
    OTHER        = "other"


class AnalysisStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"


class MessageRole(str, enum.Enum):
    USER      = "user"
    ASSISTANT = "assistant"
    SYSTEM    = "system"


# ── Users ──────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            : Mapped[str]      = mapped_column(String(36), primary_key=True, default=_uuid)
    email         : Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name     : Mapped[str]      = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str]     = mapped_column(String(255), nullable=False)
    is_active     : Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at    : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at    : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile               : Mapped[Optional["UserProfile"]]             = relationship("UserProfile",            back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents             : Mapped[List["Document"]]                    = relationship("Document",               back_populates="user", cascade="all, delete-orphan")
    resume_analyses       : Mapped[List["ResumeAnalysis"]]              = relationship("ResumeAnalysis",         back_populates="user", cascade="all, delete-orphan")
    career_roadmaps       : Mapped[List["CareerRoadmap"]]               = relationship("CareerRoadmap",          back_populates="user", cascade="all, delete-orphan")
    skill_gap_analyses    : Mapped[List["SkillGapAnalysis"]]            = relationship("SkillGapAnalysis",       back_populates="user", cascade="all, delete-orphan")
    project_recommendations: Mapped[List["ProjectRecommendation"]]      = relationship("ProjectRecommendation",  back_populates="user", cascade="all, delete-orphan")
    chat_sessions         : Mapped[List["ChatSession"]]                 = relationship("ChatSession",            back_populates="user", cascade="all, delete-orphan")
    weekly_goals          : Mapped[List["WeeklyGoal"]]                  = relationship("WeeklyGoal",             back_populates="user", cascade="all, delete-orphan")


# ── User Profile ───────────────────────────────────────────────

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id                  : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id             : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    branch              : Mapped[Optional[str]]  = mapped_column(String(255))
    semester            : Mapped[Optional[str]]  = mapped_column(String(50))
    cgpa                : Mapped[Optional[float]]= mapped_column(Float)
    headline            : Mapped[Optional[str]]  = mapped_column(String(255))
    bio                 : Mapped[Optional[str]]  = mapped_column(Text)
    location            : Mapped[Optional[str]]  = mapped_column(String(255))
    phone               : Mapped[Optional[str]]  = mapped_column(String(50))
    linkedin_url        : Mapped[Optional[str]]  = mapped_column(String(500))
    github_url          : Mapped[Optional[str]]  = mapped_column(String(500))
    experience_level    : Mapped[Optional[str]]  = mapped_column(SAEnum(ExperienceLevel))
    target_roles        : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    target_industries   : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    skills              : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    certifications      : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    education           : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    work_experience     : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    career_goals        : Mapped[Optional[str]]  = mapped_column(Text)
    profile_completeness: Mapped[float]          = mapped_column(Float, default=0.0)
    updated_at          : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="profile")


# ── Documents ──────────────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id                : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id           : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    document_type     : Mapped[str]            = mapped_column(SAEnum(DocumentType), nullable=False)
    original_filename : Mapped[str]            = mapped_column(String(500), nullable=False)
    file_path         : Mapped[str]            = mapped_column(String(1000), nullable=False)
    file_size_bytes   : Mapped[int]            = mapped_column(Integer, default=0)
    content_type      : Mapped[str]            = mapped_column(String(200))
    extracted_text    : Mapped[Optional[str]]  = mapped_column(Text)
    analysis_status   : Mapped[str]            = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    uploaded_at       : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="documents")


# ── Resume Analysis ────────────────────────────────────────────

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id             : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id        : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    document_id    : Mapped[Optional[str]]  = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"))
    summary        : Mapped[Optional[str]]  = mapped_column(Text)
    ats_score      : Mapped[Optional[float]]= mapped_column(Float)
    skills_found   : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    missing_skills : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    suggestions    : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    career_suggestions: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    raw_result     : Mapped[Optional[dict]] = mapped_column(JSON)
    tokens_used    : Mapped[int]            = mapped_column(Integer, default=0)
    status         : Mapped[str]            = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    created_at     : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="resume_analyses")


# ── Skill Gap Analysis ─────────────────────────────────────────

class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id              : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id         : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    career_goal     : Mapped[str]            = mapped_column(String(500), nullable=False)
    current_skills  : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    missing_skills  : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    priority_order  : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    learning_roadmap: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    ibm_courses     : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    weekly_plan     : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    timeline_weeks  : Mapped[Optional[int]]  = mapped_column(Integer)
    tokens_used     : Mapped[int]            = mapped_column(Integer, default=0)
    status          : Mapped[str]            = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    created_at      : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="skill_gap_analyses")


# ── Career Roadmap ─────────────────────────────────────────────

class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id                : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id           : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    current_position  : Mapped[Optional[str]]  = mapped_column(String(500))
    target_position   : Mapped[Optional[str]]  = mapped_column(String(500))
    required_skills   : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    monthly_goals     : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    ibm_certifications: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    expected_salary   : Mapped[Optional[str]]  = mapped_column(String(200))
    timeline_months   : Mapped[Optional[int]]  = mapped_column(Integer)
    future_scope      : Mapped[Optional[str]]  = mapped_column(Text)
    raw_result        : Mapped[Optional[dict]] = mapped_column(JSON)
    tokens_used       : Mapped[int]            = mapped_column(Integer, default=0)
    status            : Mapped[str]            = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    created_at        : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="career_roadmaps")


# ── Project Recommendations ────────────────────────────────────

class ProjectRecommendation(Base):
    __tablename__ = "project_recommendations"

    id               : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id          : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title            : Mapped[str]            = mapped_column(String(500), nullable=False)
    problem_statement: Mapped[Optional[str]]  = mapped_column(Text)
    tech_stack       : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    ibm_technologies : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    architecture     : Mapped[Optional[str]]  = mapped_column(Text)
    difficulty       : Mapped[Optional[str]]  = mapped_column(String(50))
    timeline_weeks   : Mapped[Optional[int]]  = mapped_column(Integer)
    github_structure : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    learning_outcomes: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    tokens_used      : Mapped[int]            = mapped_column(Integer, default=0)
    created_at       : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="project_recommendations")


# ── Chat Sessions & Messages ───────────────────────────────────

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id           : Mapped[str]      = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id      : Mapped[str]      = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title        : Mapped[str]      = mapped_column(String(500), default="New Conversation")
    context_type : Mapped[str]      = mapped_column(String(100), default="general")
    is_active    : Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at   : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at   : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user    : Mapped["User"]             = relationship("User", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]]= relationship("ChatMessage", back_populates="session",
                                                         cascade="all, delete-orphan",
                                                         order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id          : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id  : Mapped[str]            = mapped_column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role        : Mapped[str]            = mapped_column(SAEnum(MessageRole), nullable=False)
    content     : Mapped[str]            = mapped_column(Text, nullable=False)
    tokens_used : Mapped[int]            = mapped_column(Integer, default=0)
    created_at  : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")


# ── Weekly Goals ───────────────────────────────────────────────

class WeeklyGoal(Base):
    __tablename__ = "weekly_goals"

    id          : Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id     : Mapped[str]            = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_number : Mapped[int]            = mapped_column(Integer, nullable=False)
    year        : Mapped[int]            = mapped_column(Integer, nullable=False)
    goals       : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    completed   : Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    is_completed: Mapped[bool]           = mapped_column(Boolean, default=False)
    created_at  : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="weekly_goals")
