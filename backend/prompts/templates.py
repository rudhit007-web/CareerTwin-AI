"""
CareerTwin AI – IBM Granite Prompt Templates
Each function returns a fully-formed prompt string ready for the watsonx.ai API.
Granite uses instruction-following format: <|system|> ... <|user|> ... <|assistant|>
"""

SYSTEM_PROMPT = """You are CareerTwin AI, an autonomous AI Career Digital Twin built on IBM Granite.
Your mission is to help students and professionals become industry-ready by providing
personalized, accurate, and actionable career guidance.

Rules:
- Always explain WHY each recommendation matters.
- Recommend IBM SkillsBuild courses whenever applicable.
- Use uploaded document context when available.
- Return ONLY valid JSON — no markdown fences, no extra text.
- Never hallucinate skills, companies, or certifications.
- Always encourage continuous learning."""


def resume_analysis_prompt(resume_text: str, career_goal: str = "") -> str:
    goal_context = f"The candidate's career goal is: {career_goal}." if career_goal else ""
    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
Analyze the following resume and return a JSON object with exactly these keys:
- "summary": 3-4 sentence professional summary of the candidate
- "ats_score": ATS compatibility score from 0 to 100 (integer)
- "skills_found": list of skills identified in the resume
- "missing_skills": list of important skills missing for the target role
- "suggestions": list of specific resume improvement suggestions (at least 5)
- "career_suggestions": list of career development recommendations (at least 3)
- "strengths": list of candidate's key strengths
- "experience_level": one of "student", "entry", "mid", "senior"

{goal_context}

Resume:
{resume_text}

Return ONLY a valid JSON object. No explanation, no markdown.
<|assistant|>
"""


def skill_gap_analysis_prompt(career_goal: str, current_skills: list, resume_summary: str = "") -> str:
    skills_str = ", ".join(current_skills) if current_skills else "Not specified"
    resume_context = f"\nResume context: {resume_summary}" if resume_summary else ""
    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
Perform a detailed skill gap analysis for someone who wants to become a {career_goal}.

Current skills: {skills_str}{resume_context}

Return a JSON object with exactly these keys:
- "missing_skills": list of objects each with "skill", "importance" (high/medium/low), "why_needed"
- "priority_order": ordered list of skills to learn first (just skill names)
- "learning_roadmap": list of objects with "phase" (1/2/3), "duration", "skills", "goal"
- "ibm_courses": list of objects with "course_name", "platform" ("IBM SkillsBuild"), "url", "skill_covered"
- "weekly_plan": list of 4 objects (4 weeks), each with "week", "focus", "tasks" (list of strings)
- "timeline_weeks": estimated total weeks to be job-ready (integer)
- "difficulty": overall difficulty "beginner", "intermediate", or "advanced"
- "current_skills": the input skills list echoed back

Return ONLY a valid JSON object. No explanation, no markdown.
<|assistant|>
"""


def career_roadmap_prompt(profile: dict) -> str:
    name = profile.get("full_name", "the candidate")
    branch = profile.get("branch", "Computer Science")
    semester = profile.get("semester", "final year")
    cgpa = profile.get("cgpa", "N/A")
    career_goal = profile.get("career_goals", "Software Engineer")
    skills = ", ".join(profile.get("skills", [])) or "Not specified"

    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
Generate a comprehensive career roadmap for {name}.

Profile:
- Branch: {branch}
- Semester/Year: {semester}
- CGPA: {cgpa}
- Career Goal: {career_goal}
- Current Skills: {skills}

Return a JSON object with exactly these keys:
- "current_position": current status description
- "target_position": target job title
- "required_skills": list of skills needed for target role
- "monthly_goals": list of 6 objects, each with "month", "goal", "skills", "milestone"
- "ibm_certifications": list of relevant IBM certifications with "name", "relevance", "url"
- "expected_salary": salary range at target position (e.g., "$80,000 - $110,000/year")
- "timeline_months": realistic months to reach target (integer)
- "future_scope": paragraph about future growth opportunities
- "interview_tips": list of 5 preparation tips
- "key_projects": list of 3 recommended projects to build

Return ONLY a valid JSON object. No explanation, no markdown.
<|assistant|>
"""


def project_recommendation_prompt(profile: dict, skills: list, career_goal: str) -> str:
    skills_str = ", ".join(skills) if skills else "Python, JavaScript"
    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
Recommend 3 portfolio projects for a student with the following profile:
- Career Goal: {career_goal}
- Skills: {skills_str}
- Branch: {profile.get("branch", "Computer Science")}

Return a JSON object with key "projects" containing a list of 3 objects, each with:
- "title": project name
- "problem_statement": what problem it solves (2-3 sentences)
- "tech_stack": list of technologies used
- "ibm_technologies": list of IBM technologies used (e.g. watsonx.ai, IBM Cloud, Granite)
- "architecture": brief system architecture description
- "difficulty": "beginner", "intermediate", or "advanced"
- "timeline_weeks": estimated weeks to complete (integer)
- "github_structure": list of folder/file names for repo structure
- "learning_outcomes": list of skills the student will gain
- "why_this_project": explanation of career impact

Return ONLY a valid JSON object. No explanation, no markdown.
<|assistant|>
"""


def career_chat_prompt(user_message: str, history: list, profile: dict) -> str:
    name = profile.get("full_name", "the student")
    career_goal = profile.get("career_goals", "a tech professional")
    skills = ", ".join(profile.get("skills", [])) or "Not specified"
    branch = profile.get("branch", "Not specified")

    history_text = ""
    for msg in history[-6:]:  # last 6 messages for context window
        role_label = "Student" if msg["role"] == "user" else "CareerTwin AI"
        history_text += f"{role_label}: {msg['content']}\n"

    return f"""<|system|>
{SYSTEM_PROMPT}

Student profile:
- Name: {name}
- Branch: {branch}
- Career Goal: {career_goal}
- Skills: {skills}
<|user|>
Conversation history:
{history_text}

Student: {user_message}

Respond as CareerTwin AI — a professional, encouraging, and knowledgeable career mentor.
Be specific, practical, and always relate advice to the student's profile.
Recommend IBM SkillsBuild courses when relevant.
Use markdown formatting for readability (bullet points, bold, etc.).
<|assistant|>
CareerTwin AI:"""
