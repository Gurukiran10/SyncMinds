import React, { useState } from 'react'
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
  User as UserIcon,
  ChevronRight,
  Brain,
  Vote,
  Menu,
  X,
} from 'lucide-react'
import { api } from '../lib/api'
import { clearTokens } from '../lib/auth'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Separator } from '@/components/ui/separator'

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

const SidebarContent: React.FC<{ currentUser: any; onNavClick?: () => void }> = ({ currentUser, onNavClick }) => {
  const handleLogout = () => {
    clearTokens()
    window.location.href = '/login'
  }

  const initials = (currentUser?.full_name || 'User')
    .split(' ')
    .map((p: string) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-100">
        <h1 className="text-lg font-bold text-primary-600">MeetingIntel</h1>
        <p className="text-xs text-gray-400 mt-0.5">AI Meeting Assistant</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavClick}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="w-[18px] h-[18px] flex-shrink-0" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-primary-600 text-xs font-semibold">{initials}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-700 truncate">{currentUser?.full_name || 'User'}</p>
            <p className="text-xs text-gray-400 truncate">{currentUser?.role || 'Member'}</p>
          </div>
          <button
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            onClick={handleLogout}
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const { data: currentUser } = useQuery('current-user', async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:w-60 lg:flex lg:flex-col bg-white border-r border-gray-100 shadow-sm z-20">
        <SidebarContent currentUser={currentUser} />
      </div>

      {/* Mobile: overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile: sidebar drawer */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-200 ease-out lg:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="absolute top-3 right-3">
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <SidebarContent currentUser={currentUser} onNavClick={() => setSidebarOpen(false)} />
      </div>

      {/* Mobile top bar */}
      <div className="lg:hidden sticky top-0 z-30 flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-100 shadow-sm">
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-1.5 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <span className="font-bold text-primary-600 text-lg">MeetingIntel</span>
      </div>

      {/* Main content */}
      <div className="lg:pl-60">
        <main className="py-6 px-4 sm:px-6 lg:py-8 lg:px-8 page-fade">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
