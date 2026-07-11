"""
CareerTwin AI – IBM watsonx.ai / Granite AI Service
All Granite model interactions: analyze_resume, skill_gap_analysis,
generate_career_roadmap, recommend_projects, career_chat
"""

import json
import logging
import time
from typing import Optional

import httpx

from config import get_settings
from prompts.templates import (
    resume_analysis_prompt,
    skill_gap_analysis_prompt,
    career_roadmap_prompt,
    project_recommendation_prompt,
    career_chat_prompt,
)

logger = logging.getLogger(__name__)
settings = get_settings()

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
GENERATE_URL  = f"{settings.watsonx_url}/ml/v1/text/generation?version=2023-05-29"


# ── IAM Token Manager ──────────────────────────────────────────

class _TokenManager:
    """Caches and auto-refreshes IBM IAM bearer tokens."""

    def __init__(self):
        self._token: Optional[str] = None
        self._expires_at: float = 0.0

    async def get_token(self) -> str:
        if self._token and time.time() < self._expires_at - 60:
            return self._token

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                IAM_TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": settings.watsonx_api_key,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["access_token"]
            self._expires_at = time.time() + data.get("expires_in", 3600)
            logger.info("IBM IAM token refreshed.")
        return self._token


_token_manager = _TokenManager()


# ── Core generation function ───────────────────────────────────

async def _generate(
    prompt: str,
    max_new_tokens: int = 1500,
    temperature: float = 0.3,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
) -> dict:
    """
    Send a prompt to IBM Granite and return {"text": str, "tokens_used": int}.
    """
    token = await _token_manager.get_token()

    payload = {
        "model_id": settings.watsonx_model_id,
        "project_id": settings.watsonx_project_id,
        "input": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            GENERATE_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        if not resp.is_success:
            # Extract the human-readable error from watsonx response body
            try:
                err_body = resp.json()
                err_msg = err_body.get("errors", [{}])[0].get("message", resp.text)
            except Exception:
                err_msg = resp.text
            logger.error(f"watsonx API error {resp.status_code}: {err_msg}")
            from fastapi import HTTPException
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"watsonx.ai error: {err_msg}"
            )
        data = resp.json()

    result = data.get("results", [{}])[0]
    return {
        "text": result.get("generated_text", "").strip(),
        "tokens_used": result.get("generated_token_count", 0),
    }


def _parse_json(raw: str) -> dict:
    """Extract and parse JSON from Granite's response text."""
    text = raw.strip()

    # Strip markdown code fences if present
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()

    # Find the outermost JSON object
    start_idx = text.find("{")
    end_idx = text.rfind("}") + 1
    if start_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx]

    return json.loads(text)


# ── Public AI functions ────────────────────────────────────────

async def analyze_resume(resume_text: str, career_goal: str = "") -> dict:
    """
    Analyze a resume using IBM Granite.
    Returns: summary, ats_score, skills_found, missing_skills,
             suggestions, career_suggestions, strengths, experience_level
    """
    logger.info("analyze_resume: calling Granite …")
    prompt = resume_analysis_prompt(resume_text, career_goal)
    raw = await _generate(prompt, max_new_tokens=1500, temperature=0.2)

    try:
        data = _parse_json(raw["text"])
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"analyze_resume JSON parse failed: {e}\nRaw: {raw['text'][:500]}")
        # Return a safe fallback so the API doesn't crash
        data = {
            "summary": "Resume analysis could not be completed. Please retry.",
            "ats_score": 0,
            "skills_found": [],
            "missing_skills": [],
            "suggestions": ["Please retry the analysis."],
            "career_suggestions": [],
            "strengths": [],
            "experience_level": "student",
        }

    data["tokens_used"] = raw["tokens_used"]
    return data


async def skill_gap_analysis(career_goal: str, current_skills: list, resume_summary: str = "") -> dict:
    """
    Identify skill gaps between current skills and the target career goal.
    Returns: missing_skills, priority_order, learning_roadmap, ibm_courses, weekly_plan, timeline_weeks
    """
    logger.info(f"skill_gap_analysis: goal={career_goal}")
    prompt = skill_gap_analysis_prompt(career_goal, current_skills, resume_summary)
    raw = await _generate(prompt, max_new_tokens=2000, temperature=0.3)

    try:
        data = _parse_json(raw["text"])
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"skill_gap_analysis JSON parse failed: {e}")
        data = {
            "missing_skills": [],
            "priority_order": [],
            "learning_roadmap": [],
            "ibm_courses": [],
            "weekly_plan": [],
            "timeline_weeks": 12,
            "difficulty": "intermediate",
            "current_skills": current_skills,
        }

    data["tokens_used"] = raw["tokens_used"]
    return data


async def generate_career_roadmap(profile: dict) -> dict:
    """
    Generate a personalised career roadmap based on the student's full profile.
    Returns: current_position, target_position, monthly_goals, ibm_certifications,
             expected_salary, timeline_months, future_scope
    """
    logger.info(f"generate_career_roadmap: user={profile.get('full_name', 'unknown')}")
    prompt = career_roadmap_prompt(profile)
    raw = await _generate(prompt, max_new_tokens=2000, temperature=0.4)

    try:
        data = _parse_json(raw["text"])
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"generate_career_roadmap JSON parse failed: {e}")
        data = {
            "current_position": "Student",
            "target_position": profile.get("career_goals", "Software Engineer"),
            "required_skills": [],
            "monthly_goals": [],
            "ibm_certifications": [],
            "expected_salary": "Varies by location",
            "timeline_months": 12,
            "future_scope": "Please retry roadmap generation.",
            "interview_tips": [],
            "key_projects": [],
        }

    data["tokens_used"] = raw["tokens_used"]
    return data


async def recommend_projects(profile: dict, skills: list, career_goal: str) -> dict:
    """
    Recommend 3 portfolio projects aligned with skills and career goals.
    Returns: {"projects": [...]}
    """
    logger.info(f"recommend_projects: goal={career_goal}")
    prompt = project_recommendation_prompt(profile, skills, career_goal)
    raw = await _generate(prompt, max_new_tokens=2000, temperature=0.5)

    try:
        data = _parse_json(raw["text"])
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"recommend_projects JSON parse failed: {e}")
        data = {"projects": []}

    data["tokens_used"] = raw["tokens_used"]
    return data


async def career_chat(user_message: str, history: list, profile: dict) -> dict:
    """
    Conversational career mentor using IBM Granite.
    Returns: {"reply": str, "tokens_used": int}
    """
    logger.info("career_chat: generating response …")
    prompt = career_chat_prompt(user_message, history, profile)
    raw = await _generate(prompt, max_new_tokens=800, temperature=0.7)

    return {
        "reply": raw["text"],
        "tokens_used": raw["tokens_used"],
    }
