import { useRef, useState } from 'react'
import { UploadCloud, FileText } from 'lucide-react'
import clsx from 'clsx'

export default function FileUpload({ onFileSelect, uploading }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = (file) => {
    if (file) onFileSelect(file)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      className={clsx(
        'flex flex-col items-center justify-center rounded-lg border-2 border-dashed cursor-pointer py-10 px-6 transition-colors duration-150',
        dragging ? 'border-ibm-blue bg-ibm-blue/5' : 'border-ibm-gray-3 hover:border-ibm-blue hover:bg-ibm-gray-2',
        uploading && 'pointer-events-none opacity-60'
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
        disabled={uploading}
      />
      {uploading ? (
        <div className="w-8 h-8 border-2 border-ibm-gray-3 border-t-ibm-blue rounded-full animate-spin mb-3" />
      ) : (
        <UploadCloud size={32} className="text-ibm-blue mb-3" />
      )}
      <p className="text-sm font-medium text-ibm-white">
        {uploading ? 'Uploading…' : 'Drop your resume here, or click to browse'}
      </p>
      <p className="text-xs text-ibm-gray-4 mt-1">PDF, DOCX or TXT · max 10 MB</p>
    </div>
  )
}
