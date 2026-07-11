import { useState, useEffect } from 'react'
import { careerAPI } from '../api/client'
import { SectionCard, SkillTag, EmptyState } from '../components/Cards'
import Loader from '../components/Loader'
import { Zap, BookOpen, Clock, Award, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SkillGap() {
  const [careerGoal, setCareerGoal] = useState('')
  const [skills,     setSkillsInput] = useState('')
  const [analysis,   setAnalysis]   = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [fetching,   setFetching]   = useState(true)

  useEffect(() => {
    careerAPI.getSkillGap()
      .then(r => setAnalysis(r.data))
      .catch(() => {})
      .finally(() => setFetching(false))
  }, [])

  const handleRun = async (e) => {
    e.preventDefault()
    if (!careerGoal.trim()) { toast.error('Please enter a career goal.'); return }
    setLoading(true)
    try {
      const skillsList = skills.split(',').map(s => s.trim()).filter(Boolean)
      const res = await careerAPI.runSkillGap({ career_goal: careerGoal, current_skills: skillsList })
      setAnalysis(res.data)
      toast.success('Skill gap analysis complete!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) return <Loader text="Loading skill gap analysis…" />

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-ibm-white">Skill Gap Analysis</h1>
        <p className="text-ibm-gray-4 mt-1">IBM Granite identifies what skills you need for your target role.</p>
      </div>

      {/* Input form */}
      <SectionCard title="Analyse Your Skill Gap" icon={Zap}>
        <form onSubmit={handleRun} className="space-y-4">
          <div>
            <label className="label">Career Goal *</label>
            <input className="input" placeholder="e.g. Full Stack Developer, Data Scientist, DevOps Engineer" value={careerGoal} onChange={e => setCareerGoal(e.target.value)} required />
          </div>
          <div>
            <label className="label">Your Current Skills <span className="text-ibm-gray-4 font-normal">(comma-separated · leave blank to use profile)</span></label>
            <input className="input" placeholder="Python, React, SQL, Machine Learning…" value={skills} onChange={e => setSkillsInput(e.target.value)} />
          </div>
          <button type="submit" className="btn-primary flex items-center gap-2" disabled={loading}>
            {loading ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Analysing…</> : <><Zap size={15} />Run Analysis</>}
          </button>
        </form>
      </SectionCard>

      {loading && <Loader text="IBM Granite is analysing your skill gap…" />}

      {analysis && !loading && (
        <div className="space-y-6 animate-slide-up">
          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="card text-center">
              <p className="text-3xl font-bold text-ibm-red">{analysis.missing_skills?.length ?? 0}</p>
              <p className="text-sm text-ibm-gray-4 mt-1">Skills to Learn</p>
            </div>
            <div className="card text-center">
              <p className="text-3xl font-bold text-ibm-yellow">{analysis.timeline_weeks ?? '–'}</p>
              <p className="text-sm text-ibm-gray-4 mt-1">Weeks to Job-Ready</p>
            </div>
            <div className="card text-center">
              <p className="text-3xl font-bold text-ibm-cyan">{analysis.ibm_courses?.length ?? 0}</p>
              <p className="text-sm text-ibm-gray-4 mt-1">IBM SkillsBuild Courses</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Missing Skills */}
            <SectionCard title="Missing Skills (Priority Order)" icon={AlertCircle}>
              <div className="space-y-2">
                {analysis.missing_skills?.map((item, i) => (
                  <div key={i} className="flex items-start gap-3 bg-ibm-gray-2 rounded-lg px-3 py-2">
                    <span className="text-xs font-bold text-ibm-red mt-0.5 w-5 flex-shrink-0">#{i + 1}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-ibm-white">{typeof item === 'object' ? item.skill : item}</p>
                      {typeof item === 'object' && item.why_needed && (
                        <p className="text-xs text-ibm-gray-4 mt-0.5">{item.why_needed}</p>
                      )}
                      {typeof item === 'object' && item.importance && (
                        <span className={`badge mt-1 ${item.importance === 'high' ? 'badge-red' : item.importance === 'medium' ? 'badge-yellow' : 'badge-cyan'}`}>{item.importance}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>

            {/* IBM SkillsBuild Courses */}
            <SectionCard title="IBM SkillsBuild Courses" icon={Award}>
              <div className="space-y-3">
                {analysis.ibm_courses?.map((c, i) => (
                  <div key={i} className="bg-ibm-gray-2 rounded-lg p-3 border border-ibm-gray-3 hover:border-ibm-purple transition-colors">
                    <p className="text-sm font-medium text-ibm-white">{typeof c === 'object' ? c.course_name : c}</p>
                    {typeof c === 'object' && (
                      <>
                        {c.skill_covered && <p className="text-xs text-ibm-gray-4 mt-0.5">Covers: {c.skill_covered}</p>}
                        {c.url && <a href={c.url} target="_blank" rel="noopener noreferrer" className="text-xs text-ibm-cyan hover:underline mt-1 inline-block">IBM SkillsBuild →</a>}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>

          {/* Learning Roadmap */}
          <SectionCard title="Learning Roadmap" icon={BookOpen}>
            <div className="space-y-4">
              {analysis.learning_roadmap?.map((phase, i) => (
                <div key={i} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-ibm-blue flex items-center justify-center text-sm font-bold text-white flex-shrink-0">
                      {typeof phase === 'object' ? phase.phase : i + 1}
                    </div>
                    {i < (analysis.learning_roadmap.length - 1) && <div className="w-0.5 flex-1 bg-ibm-gray-3 mt-2 min-h-[24px]" />}
                  </div>
                  <div className="pb-4">
                    <p className="text-sm font-semibold text-ibm-white">{typeof phase === 'object' ? phase.goal : phase}</p>
                    {typeof phase === 'object' && (
                      <>
                        {phase.duration && <p className="text-xs text-ibm-gray-4 mt-0.5">{phase.duration}</p>}
                        {phase.skills && <div className="flex flex-wrap mt-2">{phase.skills.map(s => <SkillTag key={s} skill={s} variant="new" />)}</div>}
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          {/* 4-Week Plan */}
          <SectionCard title="4-Week Action Plan" icon={Clock}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.weekly_plan?.map((week, i) => (
                <div key={i} className="bg-ibm-gray-2 rounded-lg p-4 border border-ibm-gray-3">
                  <p className="text-sm font-bold text-ibm-blue mb-1">Week {typeof week === 'object' ? week.week : i + 1}</p>
                  {typeof week === 'object' && week.focus && <p className="text-sm font-medium text-ibm-white mb-2">{week.focus}</p>}
                  {typeof week === 'object' && week.tasks && (
                    <ul className="space-y-1">
                      {week.tasks.map((t, j) => (
                        <li key={j} className="flex items-start gap-2 text-xs text-ibm-gray-4">
                          <span className="w-1 h-1 rounded-full bg-ibm-cyan mt-1.5 flex-shrink-0" />{t}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      )}
    </div>
  )
}
