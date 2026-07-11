import clsx from 'clsx'

const COLOR_CLASSES = {
  blue:   'bg-ibm-blue',
  cyan:   'bg-ibm-cyan',
  green:  'bg-ibm-green',
  yellow: 'bg-ibm-yellow',
  red:    'bg-red-500',
  purple: 'bg-ibm-purple',
}

export default function ProgressBar({ value = 0, color = 'blue', label }) {
  const pct = Math.min(100, Math.max(0, value))
  return (
    <div>
      {label && (
        <div className="flex justify-between mb-1">
          <span className="text-xs text-ibm-gray-4">{label}</span>
          <span className="text-xs font-medium text-ibm-white">{Math.round(pct)}%</span>
        </div>
      )}
      <div className="h-1.5 bg-ibm-gray-3 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-500', COLOR_CLASSES[color] || 'bg-ibm-blue')}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
