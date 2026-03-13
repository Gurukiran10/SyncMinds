import React from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  LayoutDashboard,
  Calendar,
  CheckSquare,
  Bell,
  BarChart3,
  Settings,
  LogOut,
  Plug,
  Brain,
  Vote,
} from 'lucide-react'
import { api } from '../lib/api'
import { clearTokens } from '../lib/auth'

const Layout: React.FC = () => {
  const { data: currentUser } = useQuery('current-user', async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  })

  const handleLogout = () => {
    clearTokens()
    window.location.href = '/login'
  }

  const navigation = [
    { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
    { name: 'Meetings', to: '/meetings', icon: Calendar },
    { name: 'Action Items', to: '/action-items', icon: CheckSquare },
    { name: 'Mentions', to: '/mentions', icon: Bell },
    { name: 'Analytics', to: '/analytics', icon: BarChart3 },
    { name: 'Decisions', to: '/decisions', icon: Vote },
    { name: 'Knowledge', to: '/knowledge', icon: Brain },
    { name: 'Integrations', to: '/integrations', icon: Plug },
    { name: 'Settings', to: '/settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="px-6 py-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-primary-600">
              MeetingIntel
            </h1>
            <p className="text-sm text-gray-500 mt-1">AI Meeting Assistant</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* User section */}
          <div className="px-4 py-4 border-t border-gray-200">
            <div className="flex items-center px-4 py-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-primary-600 font-medium">
                    {(currentUser?.full_name || 'User')
                      .split(' ')
                      .map((p: string) => p[0])
                      .join('')
                      .slice(0, 2)
                      .toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-700">{currentUser?.full_name || 'User'}</p>
                <p className="text-xs text-gray-500">{currentUser?.role || 'Member'}</p>
              </div>
              <button className="text-gray-400 hover:text-gray-600" onClick={handleLogout}>
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-8 px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
