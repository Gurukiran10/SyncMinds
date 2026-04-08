import React, { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Brain, CheckCircle, Zap, Users } from 'lucide-react'
import { api } from '../lib/api'
import { isAuthenticated, setTokens } from '../lib/auth'

const features = [
  { icon: Brain, text: 'AI-powered transcription & summaries' },
  { icon: CheckCircle, text: 'Auto-extracted action items & decisions' },
  { icon: Zap, text: 'Semantic search across all meetings' },
  { icon: Users, text: 'Team-wide insights & analytics' },
]

const Login: React.FC = () => {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />
  }

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      const response = await api.post('/api/v1/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      setTokens(response.data.access_token, response.data.refresh_token)
      window.location.href = '/dashboard'
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">SyncMinds</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight mb-4">
            Turn every meeting into<br />actionable intelligence
          </h2>
          <p className="text-primary-200 text-lg">
            AI transcribes, summarizes, and extracts action items so your team can focus on what matters.
          </p>
        </div>
        <div className="space-y-4">
          {features.map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon className="w-4 h-4 text-white" />
              </div>
              <span className="text-primary-100 text-sm">{text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">SyncMinds</span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-1">Welcome back</h1>
          <p className="text-sm text-gray-500 mb-8">Sign in to your workspace</p>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none transition-colors"
                placeholder="Enter your username"
                required
                autoFocus
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none transition-colors"
                placeholder="Enter your password"
                required
              />
            </div>

            {error && (
              <div className="px-3.5 py-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-xs text-gray-400 text-center">
            Demo: <span className="font-mono">admin / admin123</span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
