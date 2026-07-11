export default function Loader({ text = 'Loading…', size = 'md' }) {
  const spinnerSize = size === 'lg' ? 'w-10 h-10 border-4' : 'w-7 h-7 border-2'
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className={`${spinnerSize} border-ibm-gray-3 border-t-ibm-blue rounded-full animate-spin`} />
      <p className="text-sm text-ibm-gray-4">{text}</p>
    </div>
  )
}
