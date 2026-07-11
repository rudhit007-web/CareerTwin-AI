import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, User, FileText, Zap, Map,
  FolderGit2, MessageSquare, LogOut, ChevronLeft, ChevronRight,
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/',          label: 'Dashboard',  icon: LayoutDashboard },
  { to: '/profile',   label: 'Profile',    icon: User },
  { to: '/resume',    label: 'Resume',     icon: FileText },
  { to: '/skill-gap', label: 'Skill Gap',  icon: Zap },
  { to: '/roadmap',   label: 'Roadmap',    icon: Map },
  { to: '/projects',  label: 'Projects',   icon: FolderGit2 },
  { to: '/chat',      label: 'AI Chat',    icon: MessageSquare },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  return (
    <div className="flex h-screen bg-ibm-dark overflow-hidden">
      {/* Sidebar */}
      <aside className={clsx(
        'flex flex-col bg-ibm-gray border-r border-ibm-gray-3 transition-all duration-200 flex-shrink-0',
        collapsed ? 'w-14' : 'w-52'
      )}>
        {/* Brand */}
        <div className={clsx('flex items-center gap-2 px-3 py-4 border-b border-ibm-gray-3', collapsed ? 'justify-center' : 'justify-between')}>
          {!collapsed && (
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded bg-ibm-blue flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold text-white">C</span>
              </div>
              <span className="text-sm font-bold text-ibm-white truncate">CareerTwin AI</span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(c => !c)}
            className="text-ibm-gray-4 hover:text-ibm-white transition-colors flex-shrink-0"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 py-2 space-y-0.5 px-1.5 overflow-y-auto">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => clsx(
                'flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm transition-colors duration-150',
                isActive
                  ? 'bg-ibm-blue/20 text-ibm-blue border border-ibm-blue/30'
                  : 'text-ibm-gray-4 hover:bg-ibm-gray-2 hover:text-ibm-white',
                collapsed && 'justify-center'
              )}
              title={collapsed ? label : undefined}
            >
              <Icon size={16} className="flex-shrink-0" />
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User / Logout */}
        <div className={clsx('border-t border-ibm-gray-3 p-2', collapsed && 'flex justify-center')}>
          {!collapsed && user && (
            <div className="px-2 py-1.5 mb-1">
              <p className="text-xs font-medium text-ibm-white truncate">{user.full_name}</p>
              <p className="text-xs text-ibm-gray-4 truncate">{user.email}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={clsx(
              'flex items-center gap-2 text-ibm-gray-4 hover:text-red-400 text-xs px-2 py-1.5 rounded hover:bg-ibm-gray-2 transition-colors w-full',
              collapsed && 'justify-center'
            )}
            title={collapsed ? 'Sign out' : undefined}
          >
            <LogOut size={14} />
            {!collapsed && 'Sign out'}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
