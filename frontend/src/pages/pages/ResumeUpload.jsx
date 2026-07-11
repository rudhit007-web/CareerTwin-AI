import { useState } from 'react'
import { resumeAPI } from '../api/client'
import { SectionCard, SkillTag } from '../components/Cards'
import FileUpload from '../components/FileUpload'
import ProgressBar from '../components/ProgressBar'
import Loader from '../components/Loader'
import { FileText, Zap, Star, ChevronRight, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ResumeUpload() {
  const [uploadedDoc, setUploadedDoc]     = useState(null)
  const [analysis,    setAnalysis]        = useState(null)
  const [uploading,   setUploading]       = useState(false)
  const [analysing,   setAnalysing]       = useState(false)

  const handleUpload = async (file) => {
    setUploading(true)
    try {
      const res = await resumeAPI.upload(file)
      setUploadedDoc(res.data)
      toast.success('Resume uploaded and text extracted!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  const handleAnalyse = async () => {
    setAnalysing(true)
    try {
      const res = await resumeAPI.analyze()
      setAnalysis(res.data)
      toast.success('Resume analysed by IBM Granite!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed.')
    } finally {
      setAnalysing(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-ibm-white">Resume Upload & Analysis</h1>
        <p className="text-ibm-gray-4 mt-1">Upload your resume · IBM Granite extracts skills and provides ATS feedback.</p>
      </div>

      {/* Upload */}
      <SectionCard title="Upload Resume" icon={FileText}>
        <FileUpload onFileSelect={handleUpload} uploading={uploading} />
        {uploadedDoc && (
          <div className="mt-4 flex items-center justify-between bg-ibm-gray-2 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3">
              <CheckCircle size={18} className="text-ibm-green" />
              <div>
                <p className="text-sm font-medium text-ibm-white">{uploadedDoc.filename}</p>
                <p className="text-xs text-ibm-gray-4">{uploadedDoc.extracted_chars?.toLocaleString()} characters extracted</p>
              </div>
            </div>
            <button onClick={handleAnalyse} className="btn-primary flex items-center gap-2 text-sm" disabled={analysing}>
              {analysing ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Analysing…</> : <><Zap size={14} /> Analyse with Granite</>}
            </button>
          </div>
        )}
        {!uploadedDoc && !uploading && (
          <div className="mt-4 text-center">
            <button onClick={handleAnalyse} className="btn-secondary text-sm" disabled={analysing}>
              {analysing ? 'Analysing…' : 'Analyse Existing Resume'}
            </button>
          </div>
        )}
      </SectionCard>

      {/* Analysis Results */}
      {analysing && <Loader text="IBM Granite is analysing your resume…" />}

      {analysis && (
        <div className="space-y-6 animate-slide-up">
          {/* ATS Score */}
          <SectionCard title="ATS Compatibility Score" icon={Star}>
            <div className="mb-4">
              <div className="flex items-end gap-3 mb-3">
                <span className="text-5xl font-bold text-ibm-white">{analysis.ats_score}</span>
                <span className="text-ibm-gray-4 mb-1">/100</span>
              </div>
              <ProgressBar
                value={analysis.ats_score}
                color={analysis.ats_score >= 70 ? 'green' : analysis.ats_score >= 50 ? 'yellow' : 'red'}
              />
            </div>
            <div className="bg-ibm-gray-2 rounded-lg p-4 mt-4">
              <p className="text-xs text-ibm-gray-4 mb-1">Professional Summary</p>
              <p className="text-sm text-ibm-white leading-relaxed">{analysis.summary}</p>
            </div>
          </SectionCard>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Skills found */}
            <SectionCard title="Skills Found" icon={CheckCircle}>
              <div className="flex flex-wrap">
                {analysis.skills_found?.map(s => <SkillTag key={s} skill={s} variant="default" />)}
              </div>
            </SectionCard>

            {/* Missing skills */}
            <SectionCard title="Missing Skills" icon={Zap}>
              <div className="flex flex-wrap">
                {analysis.missing_skills?.map(s => <SkillTag key={s} skill={s} variant="missing" />)}
              </div>
            </SectionCard>
          </div>

          {/* Suggestions */}
          <SectionCard title="Resume Improvement Suggestions" icon={ChevronRight}>
            <ul className="space-y-2">
              {analysis.suggestions?.map((s, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-ibm-white">
                  <span className="w-5 h-5 rounded bg-ibm-blue/20 text-ibm-blue text-xs flex items-center justify-center flex-shrink-0 mt-0.5 font-bold">{i + 1}</span>
                  {s}
                </li>
              ))}
            </ul>
          </SectionCard>

          {/* Career suggestions */}
          <SectionCard title="Career Development Suggestions" icon={ChevronRight}>
            <ul className="space-y-2">
              {analysis.career_suggestions?.map((s, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-ibm-white">
                  <span className="w-5 h-5 rounded bg-ibm-cyan/20 text-ibm-cyan text-xs flex items-center justify-center flex-shrink-0 mt-0.5 font-bold">{i + 1}</span>
                  {s}
                </li>
              ))}
            </ul>
          </SectionCard>
        </div>
      )}
    </div>
  )
}
