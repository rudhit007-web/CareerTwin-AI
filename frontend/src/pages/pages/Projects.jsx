import { useState, useEffect } from 'react'
import { careerAPI } from '../api/client'
import { SectionCard, SkillTag, EmptyState } from '../components/Cards'
import Loader from '../components/Loader'
import { FolderGit2, Code, Layers, Clock, ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

function ProjectCard({ project }) {
  const [expanded, setExpanded] = useState(false)

  const difficultyColor = {
    beginner: 'badge-green',
    intermediate: 'badge-yellow',
    advanced: 'badge-red',
  }[project.difficulty] || 'badge-blue'

  return (
    <div className="card-hover animate-slide-up">
      <div className="flex items-start justify-between gap-4 mb-3">
        <h3 className="text-base font-bold text-ibm-white leading-tight">{project.title}</h3>
        <div className="flex gap-2 flex-shrink-0">
          <span className={`badge ${difficultyColor}`}>{project.difficulty}</span>
          <span className="badge badge-cyan flex items-center gap-1"><Clock size={10} />{project.timeline_weeks}w</span>
        </div>
      </div>

      <p className="text-sm text-ibm-gray-4 leading-relaxed mb-4">{project.problem_statement}</p>

      <div className="mb-4">
        <p className="text-xs text-ibm-gray-4 mb-2">IBM Technologies</p>
        <div className="flex flex-wrap">
          {project.ibm_technologies?.map(t => <SkillTag key={t} skill={t} variant="ibm" />)}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-xs text-ibm-gray-4 mb-2">Tech Stack</p>
        <div className="flex flex-wrap">
          {project.tech_stack?.map(t => <SkillTag key={t} skill={t} variant="default" />)}
        </div>
      </div>

      <button
        onClick={() => setExpanded(e => !e)}
        className="btn-ghost w-full text-sm flex items-center justify-center gap-2"
      >
        {expanded ? <><ChevronUp size={14} />Less details</> : <><ChevronDown size={14} />More details</>}
      </button>

      {expanded && (
        <div className="mt-4 space-y-4 animate-slide-up border-t border-ibm-gray-3 pt-4">
          {project.architecture && (
            <div>
              <p className="text-xs text-ibm-gray-4 mb-1">Architecture</p>
              <p className="text-sm text-ibm-white leading-relaxed">{project.architecture}</p>
            </div>
          )}
          {project.github_structure?.length > 0 && (
            <div>
              <p className="text-xs text-ibm-gray-4 mb-2">GitHub Structure</p>
              <div className="bg-ibm-dark rounded-lg p-3 font-mono text-xs text-ibm-green space-y-0.5">
                <p>📁 project-root/</p>
                {project.github_structure.map((f, i) => (
                  <p key={i} className="pl-4">├── {f}</p>
                ))}
              </div>
            </div>
          )}
          {project.learning_outcomes?.length > 0 && (
            <div>
              <p className="text-xs text-ibm-gray-4 mb-2">Learning Outcomes</p>
              <ul className="space-y-1">
                {project.learning_outcomes.map((o, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-ibm-white">
                    <span className="w-1.5 h-1.5 rounded-full bg-ibm-green mt-2 flex-shrink-0" />{o}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Projects() {
  const [projects,  setProjects]  = useState([])
  const [goal,      setGoal]      = useState('')
  const [loading,   setLoading]   = useState(false)
  const [fetching,  setFetching]  = useState(true)

  useEffect(() => {
    careerAPI.getProjects()
      .then(r => setProjects(r.data.projects || []))
      .catch(() => {})
      .finally(() => setFetching(false))
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await careerAPI.runProjects(goal ? { career_goal: goal } : {})
      setProjects(res.data.projects || [])
      toast.success('Project recommendations ready!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate projects.')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) return <Loader text="Loading project recommendations…" />

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-ibm-white">Project Recommendations</h1>
        <p className="text-ibm-gray-4 mt-1">IBM Granite recommends portfolio projects with IBM technologies to accelerate your career.</p>
      </div>

      <SectionCard title="Generate Recommendations" icon={Sparkles}>
        <form onSubmit={handleGenerate} className="flex gap-3">
          <input
            className="input flex-1"
            placeholder="Optional: override career goal (e.g. AI Engineer, Cloud Architect)"
            value={goal}
            onChange={e => setGoal(e.target.value)}
          />
          <button type="submit" className="btn-primary flex-shrink-0 flex items-center gap-2" disabled={loading}>
            {loading ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Generating…</> : <><Sparkles size={15} />Generate</>}
          </button>
        </form>
      </SectionCard>

      {loading && <Loader text="IBM Granite is crafting your project ideas…" />}

      {!loading && projects.length === 0 && (
        <EmptyState
          icon={FolderGit2}
          title="No projects yet"
          description="Click Generate to get 3 personalised portfolio project recommendations using IBM technologies."
        />
      )}

      {!loading && projects.length > 0 && (
        <div className="space-y-5">
          {projects.map(p => <ProjectCard key={p.id || p.title} project={p} />)}
        </div>
      )}
    </div>
  )
}
