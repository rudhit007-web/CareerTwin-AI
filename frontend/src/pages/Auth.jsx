import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Auth() {
  const { login, register } = useAuth()
  const [mode, setMode]     = useState('login')   // 'login' | 'register'
  const [form, setForm]     = useState({ email: '', password: '', fullName: '' })
  const [loading, setLoading] = useState(false)

  const f = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
        toast.success('Welcome back!')
      } else {
        await register(form.email, form.fullName, form.password)
        toast.success('Account created! Welcome to CareerTwin AI.')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ibm-dark flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo / header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-ibm-blue flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-bold text-white">C</span>
          </div>
          <h1 className="text-2xl font-bold text-ibm-white">CareerTwin AI</h1>
          <p className="text-ibm-gray-4 text-sm mt-1">Powered by IBM Granite · watsonx.ai</p>
        </div>

        <div className="card">
          <div className="flex mb-6 bg-ibm-gray-2 rounded-lg p-1">
            {['login', 'register'].map(m => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 text-sm py-1.5 rounded-md transition-colors duration-150 font-medium ${
                  mode === m ? 'bg-ibm-blue text-white' : 'text-ibm-gray-4 hover:text-ibm-white'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="label">Full Name</label>
                <input className="input" placeholder="John Doe" value={form.fullName} onChange={f('fullName')} required />
              </div>
            )}
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={f('email')} required />
            </div>
            <div>
              <label className="label">Password</label>
              <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={f('password')} required minLength={6} />
            </div>
            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2 mt-2" disabled={loading}>
              {loading
                ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Processing…</>
                : mode === 'login' ? 'Sign In' : 'Create Account'
              }
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-ibm-gray-4 mt-6">
          Your AI career twin built on IBM Granite
        </p>
      </div>
    </div>
  )
}
