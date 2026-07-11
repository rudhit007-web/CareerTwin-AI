import { useState, useEffect } from 'react'
import { profileAPI } from '../api/client'
import { SectionCard } from '../components/Cards'
import ProgressBar from '../components/ProgressBar'
import Loader from '../components/Loader'
import { User, Save, Plus, X } from 'lucide-react'
import toast from 'react-hot-toast'

const EXPERIENCE_LEVELS = ['student', 'entry', 'mid', 'senior', 'executive']

function TagInput({ values = [], onChange, placeholder }) {
  const [input, setInput] = useState('')

  const add = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && input.trim()) {
      e.preventDefault()
      const val = input.trim().replace(/,$/, '')
      if (val && !values.includes(val)) onChange([...values, val])
      setInput('')
    }
  }
  const remove = (v) => onChange(values.filter(x => x !== v))

  return (
    <div className="flex flex-wrap gap-1.5 bg-ibm-gray-2 border border-ibm-gray-3 rounded px-3 py-2 focus-within:border-ibm-blue transition-colors min-h-[42px]">
      {values.map(v => (
        <span key={v} className="flex items-center gap-1 badge badge-blue text-xs">
          {v}
          <button type="button" onClick={() => remove(v)} className="hover:text-red-400"><X size={10} /></button>
        </span>
      ))}
      <input
        className="bg-transparent outline-none text-ibm-white text-sm flex-1 min-w-[120px] placeholder-ibm-gray-4"
        placeholder={placeholder}
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={add}
      />
    </div>
  )
}

export default function Profile() {
  const [form, setForm]     = useState({
    branch: '', semester: '', cgpa: '', headline: '', bio: '',
    location: '', phone: '', linkedin_url: '', github_url: '',
    experience_level: 'student', career_goals: '',
    skills: [], certifications: [], target_roles: [], target_industries: [],
  })
  const [completeness, setCompleteness] = useState(0)
  const [loading,  setLoading]  = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    profileAPI.get()
      .then(r => {
        const p = r.data.profile
        setForm(f => ({ ...f, ...p }))
        setCompleteness(p.profile_completeness || 0)
      })
      .catch(() => {})
      .finally(() => setFetching(false))
  }, [])

  const handleSave = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = { ...form, cgpa: form.cgpa ? parseFloat(form.cgpa) : undefined }
      const res = await profileAPI.update(payload)
      setCompleteness(res.data.profile_completeness)
      toast.success('Profile saved!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save profile.')
    } finally {
      setLoading(false)
    }
  }

  const f = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))
  const fArr = (k) => (val) => setForm(p => ({ ...p, [k]: val }))

  if (fetching) return <Loader text="Loading your profile…" />

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ibm-white">My Profile</h1>
          <p className="text-ibm-gray-4 mt-1">Complete your profile for better AI recommendations.</p>
        </div>
      </div>

      {/* Completeness */}
      <SectionCard>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-ibm-blue flex items-center justify-center text-xl font-bold text-white flex-shrink-0">
            {Math.round(completeness)}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-ibm-white mb-1.5">Profile Completeness</p>
            <ProgressBar value={completeness} color={completeness >= 70 ? 'green' : completeness >= 40 ? 'yellow' : 'red'} />
          </div>
        </div>
      </SectionCard>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Academic Info */}
        <SectionCard title="Academic Information" icon={User}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Branch / Major</label>
              <input className="input" placeholder="Computer Science" value={form.branch || ''} onChange={f('branch')} />
            </div>
            <div>
              <label className="label">Semester / Year</label>
              <input className="input" placeholder="6th Semester / 3rd Year" value={form.semester || ''} onChange={f('semester')} />
            </div>
            <div>
              <label className="label">CGPA</label>
              <input className="input" type="number" step="0.01" min="0" max="10" placeholder="8.5" value={form.cgpa || ''} onChange={f('cgpa')} />
            </div>
          </div>
          <div className="mt-4">
            <label className="label">Experience Level</label>
            <select className="input" value={form.experience_level || 'student'} onChange={f('experience_level')}>
              {EXPERIENCE_LEVELS.map(l => <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
            </select>
          </div>
        </SectionCard>

        {/* Personal Info */}
        <SectionCard title="Personal Information" icon={User}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Professional Headline</label>
              <input className="input" placeholder="Full Stack Developer | IBM Enthusiast" value={form.headline || ''} onChange={f('headline')} />
            </div>
            <div>
              <label className="label">Location</label>
              <input className="input" placeholder="Mumbai, India" value={form.location || ''} onChange={f('location')} />
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" placeholder="+91 9876543210" value={form.phone || ''} onChange={f('phone')} />
            </div>
            <div>
              <label className="label">LinkedIn URL</label>
              <input className="input" placeholder="https://linkedin.com/in/yourname" value={form.linkedin_url || ''} onChange={f('linkedin_url')} />
            </div>
            <div>
              <label className="label">GitHub URL</label>
              <input className="input" placeholder="https://github.com/yourname" value={form.github_url || ''} onChange={f('github_url')} />
            </div>
          </div>
          <div className="mt-4">
            <label className="label">Bio</label>
            <textarea className="input" rows={3} placeholder="Tell us about yourself…" value={form.bio || ''} onChange={f('bio')} />
          </div>
        </SectionCard>

        {/* Career Goals */}
        <SectionCard title="Career Goals & Skills" icon={User}>
          <div className="mb-4">
            <label className="label">Career Goals *</label>
            <textarea className="input" rows={2} placeholder="e.g. Become a Full Stack Developer with expertise in AI/ML and IBM Cloud technologies…" value={form.career_goals || ''} onChange={f('career_goals')} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Skills <span className="text-ibm-gray-4 font-normal">(press Enter to add)</span></label>
              <TagInput values={form.skills || []} onChange={fArr('skills')} placeholder="Python, React, SQL…" />
            </div>
            <div>
              <label className="label">Certifications</label>
              <TagInput values={form.certifications || []} onChange={fArr('certifications')} placeholder="IBM Cloud Essentials…" />
            </div>
            <div>
              <label className="label">Target Roles</label>
              <TagInput values={form.target_roles || []} onChange={fArr('target_roles')} placeholder="Software Engineer…" />
            </div>
            <div>
              <label className="label">Target Industries</label>
              <TagInput values={form.target_industries || []} onChange={fArr('target_industries')} placeholder="FinTech, HealthTech…" />
            </div>
          </div>
        </SectionCard>

        <div className="flex justify-end">
          <button type="submit" className="btn-primary flex items-center gap-2 px-8" disabled={loading}>
            {loading ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Saving…</> : <><Save size={15} />Save Profile</>}
          </button>
        </div>
      </form>
    </div>
  )
}