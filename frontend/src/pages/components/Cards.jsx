import clsx from 'clsx'

// ── StatCard ────────────────────────────────────────────────────
export function StatCard({ icon: Icon, label, value, color = 'blue', sub }) {
  const colors = {
    blue:   'text-ibm-blue   bg-ibm-blue/10',
    cyan:   'text-ibm-cyan   bg-ibm-cyan/10',
    green:  'text-ibm-green  bg-ibm-green/10',
    yellow: 'text-ibm-yellow bg-ibm-yellow/10',
    purple: 'text-ibm-purple bg-ibm-purple/10',
    red:    'text-red-400    bg-red-900/20',
  }
  return (
    <div className="card">
      <div className="flex items-start gap-3">
        <div className={clsx('w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0', colors[color])}>
          <Icon size={18} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs text-ibm-gray-4 truncate">{label}</p>
          <p className="text-2xl font-bold text-ibm-white mt-0.5">{value}</p>
          {sub && <p className="text-xs text-ibm-gray-4 mt-0.5">{sub}</p>}
        </div>
      </div>
    </div>
  )
}

// ── SectionCard ─────────────────────────────────────────────────
export function SectionCard({ title, icon: Icon, children, className }) {
  return (
    <div className={clsx('card', className)}>
      {(title || Icon) && (
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-ibm-gray-3">
          {Icon && <Icon size={16} className="text-ibm-blue flex-shrink-0" />}
          {title && <h2 className="text-sm font-semibold text-ibm-white">{title}</h2>}
        </div>
      )}
      {children}
    </div>
  )
}

// ── SkillTag ────────────────────────────────────────────────────
const VARIANT_CLASSES = {
  default: 'bg-ibm-gray-3 text-ibm-white',
  missing: 'bg-red-900/30 text-red-400 border border-red-900/50',
  new:     'bg-ibm-green/10 text-ibm-green border border-ibm-green/30',
  ibm:     'bg-ibm-blue/10 text-ibm-cyan border border-ibm-blue/30',
}

export function SkillTag({ skill, variant = 'default' }) {
  return (
    <span className={clsx('text-xs font-medium px-2.5 py-1 rounded-full mr-1.5 mb-1.5', VARIANT_CLASSES[variant])}>
      {skill}
    </span>
  )
}

// ── EmptyState ──────────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-12 px-6">
      {Icon && (
        <div className="w-14 h-14 rounded-2xl bg-ibm-gray-2 border border-ibm-gray-3 flex items-center justify-center mb-4">
          <Icon size={24} className="text-ibm-gray-4" />
        </div>
      )}
      <h3 className="text-base font-semibold text-ibm-white mb-1">{title}</h3>
      {description && <p className="text-sm text-ibm-gray-4 mb-4 max-w-xs">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  )
}
