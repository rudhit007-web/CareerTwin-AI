import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardAPI } from './api/client'
import { StatCard, SectionCard, SkillTag, EmptyState } from './components/Cards'
import ProgressBar from './components/ProgressBar'
import Loader from './components/Loader'
import {
  Target, FileText, Zap, Map, FolderGit2, TrendingUp,
  Award, ChevronRight, RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchDashboard = async () => {
    setLoading(true)
    try {
      const res = await dashboardAPI.get()
      setData(res.data)
    } catch {
      toast.error('Could not load dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDashboard() }, [])

  if (loading) return <Loader text="Loading your career dashboard…" size="lg" />

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ibm-white">
            Welcome back, {data?.user?.full_name?.split(' ')[0] || 'there'} 👋
          </h1>
          <p className="text-ibm-gray-4 mt-1">Here's your career readiness snapshot powered by IBM Granite.</p>
        </div>
        <button onClick={fetchDashboard} className="btn-ghost flex items-center gap-2 text-sm">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Target}    label="Career Readiness"   value={`${data?.career_readiness_score ?? 0}%`} color="blue"   sub="Overall score" />
        <StatCard icon={FileText}  label="ATS Resume Score"   value={data?.resume?.ats_score != null ? `${data.resume.ats_score}%` : '–'} color="cyan"   sub="Last analysis" />
        <StatCard icon={Zap}       label="Skills Identified"  value={data?.resume?.skills_found?.length ?? 0} color="green"  sub="From resume" />
        <StatCard icon={TrendingUp} label="Missing Skills"    value={data?.skill_gap?.missing_skills_count ?? 0} color="yellow" sub="To learn" />
      </div>

      {/* Readiness progress */}
      <SectionCard title="Career Readiness Breakdown" icon={Target}>
        <div className="space-y-4">
          <ProgressBar label="Profile Completeness" value={data?.profile_completeness ?? 0} color="blue" />
          <ProgressBar label="Resume ATS Score"      value={data?.resume?.ats_score ?? 0}    color="cyan" />
          <ProgressBar
            label="Skill Coverage"
            value={data?.skill_gap?.missing_skills_count != null
              ? Math.max(0, 100 - data.skill_gap.missing_skills_count * 10) : 0}
            color="green"
          />
          <ProgressBar label="Overall Readiness" value={data?.career_readiness_score ?? 0} color="purple" />
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Skills */}
        <SectionCard title="Current Skills" icon={Zap}>
          {data?.current_skills?.length > 0 ? (
            <div className="flex flex-wrap">
              {data.current_skills.map(s => <SkillTag key={s} skill={s} variant="default" />)}
            </div>
          ) : (
            <EmptyState
              icon={Zap}
              title="No skills found"
              description="Upload and analyse your resume to extract your skills."
              action={<Link to="/resume" className="btn-primary text-sm">Upload Resume</Link>}
            />
          )}
        </SectionCard>

        {/* Missing Skills */}
        <SectionCard title="Top Missing Skills" icon={Award}>
          {data?.skill_gap?.top_missing?.length > 0 ? (
            <div className="flex flex-wrap">
              {data.skill_gap.top_missing.map(s => <SkillTag key={s} skill={s} variant="missing" />)}
            </div>
          ) : (
            <EmptyState
              icon={Zap}
              title="No gaps found"
              description="Run a skill gap analysis to see what you need to learn."
              action={<Link to="/skill-gap" className="btn-primary text-sm">Analyse Skills</Link>}
            />
          )}
        </SectionCard>

        {/* Roadmap snapshot */}
        <SectionCard title="Career Roadmap" icon={Map}>
          {data?.roadmap?.target_position ? (
            <div className="space-y-3">
              <div>
                <p className="text-xs text-ibm-gray-4 mb-1">Current Position</p>
                <p className="text-ibm-white font-medium">{data.roadmap.current_position}</p>
              </div>
              <div className="flex items-center gap-2 text-ibm-blue">
                <ChevronRight size={16} />
              </div>
              <div>
                <p className="text-xs text-ibm-gray-4 mb-1">Target Position</p>
                <p className="text-ibm-white font-medium">{data.roadmap.target_position}</p>
              </div>
              <div className="pt-2 border-t border-ibm-gray-2 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-ibm-gray-4">Timeline</p>
                  <p className="text-sm text-ibm-white font-medium">{data.roadmap.timeline_months} months</p>
                </div>
                <div>
                  <p className="text-xs text-ibm-gray-4">Expected Salary</p>
                  <p className="text-sm text-ibm-green font-medium">{data.roadmap.expected_salary || '–'}</p>
                </div>
              </div>
              <Link to="/roadmap" className="btn-secondary text-sm w-full text-center block mt-2">View Full Roadmap</Link>
            </div>
          ) : (
            <EmptyState
              icon={Map}
              title="No roadmap yet"
              description="Generate your personalised career roadmap."
              action={<Link to="/roadmap" className="btn-primary text-sm">Generate Roadmap</Link>}
            />
          )}
        </SectionCard>

        {/* Weekly Goal */}
        <SectionCard title="This Week's Goals" icon={Target}>
          {data?.weekly_goal?.goals?.length > 0 ? (
            <ul className="space-y-2">
              {data.weekly_goal.goals.slice(0, 5).map((g, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-ibm-white">
                  <span className="w-1.5 h-1.5 rounded-full bg-ibm-blue mt-2 flex-shrink-0" />
                  {g}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              icon={Target}
              title="No goals set"
              description="Run a skill gap analysis to get your weekly plan."
              action={<Link to="/skill-gap" className="btn-primary text-sm">Analyse Skill Gap</Link>}
            />
          )}
        </SectionCard>
      </div>

      {/* Recommended Projects */}
      {data?.projects?.length > 0 && (
        <SectionCard title="Recommended Projects" icon={FolderGit2}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.projects.map(p => (
              <div key={p.id} className="bg-ibm-gray-2 rounded-lg p-4 border border-ibm-gray-3 hover:border-ibm-blue transition-colors duration-150">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-sm font-semibold text-ibm-white leading-tight">{p.title}</h3>
                  <span className={`badge flex-shrink-0 ${p.difficulty === 'beginner' ? 'badge-green' : p.difficulty === 'advanced' ? 'badge-red' : 'badge-yellow'}`}>
                    {p.difficulty}
                  </span>
                </div>
                <p className="text-xs text-ibm-gray-4 mb-3">{p.timeline_weeks} weeks</p>
                <div className="flex flex-wrap">
                  {p.ibm_technologies?.slice(0, 2).map(t => <SkillTag key={t} skill={t} variant="ibm" />)}
                </div>
              </div>
            ))}
          </div>
          <Link to="/projects" className="btn-secondary text-sm mt-4 inline-block">View All Projects</Link>
        </SectionCard>
      )}
    </div>
  )
}
