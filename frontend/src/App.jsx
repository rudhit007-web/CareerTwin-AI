import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Loader from './pages/components/Loader'

import Auth      from './pages/Auth'
import Layout    from './pages/Layout'
import Dashboard from './pages/Dashboard'
import Profile   from './pages/pages/Profile'
import ResumeUpload from './pages/pages/ResumeUpload'
import SkillGap  from './pages/pages/SkillGap'
import Roadmap   from './pages/pages/Roadmap'
import Projects  from './pages/pages/Projects'
import Chat      from './pages/pages/Chat'

function ProtectedRoutes() {
  const { user, loading } = useAuth()
  if (loading) return <Loader text="Authenticating…" size="lg" />
  if (!user)   return <Navigate to="/auth" replace />
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index       element={<Dashboard />} />
        <Route path="profile"   element={<Profile />} />
        <Route path="resume"    element={<ResumeUpload />} />
        <Route path="skill-gap" element={<SkillGap />} />
        <Route path="roadmap"   element={<Roadmap />} />
        <Route path="projects"  element={<Projects />} />
        <Route path="chat"      element={<Chat />} />
      </Route>
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/auth" element={<PublicRoute><Auth /></PublicRoute>} />
        <Route path="/*"   element={<ProtectedRoutes />} />
      </Routes>
    </AuthProvider>
  )
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Loader text="Loading…" size="lg" />
  if (user)    return <Navigate to="/" replace />
  return children
}
