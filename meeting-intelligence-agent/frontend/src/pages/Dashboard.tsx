import React from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { Calendar, Clock, TrendingUp, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'
import { SkeletonCard, SkeletonRow } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  in_progress: 'bg-blue-100 text-blue-700',
  scheduled: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-700',
}

const priorityColors: Record<string, string> = {
  urgent: 'text-red-500',
  high: 'text-orange-500',
  medium: 'text-yellow-500',
  low: 'text-gray-400',
}

const Dashboard: React.FC = () => {
  const { data: analytics, isLoading: loadingAnalytics } = useQuery('analytics', async () => {
    const response = await api.get('/api/v1/analytics/dashboard')
    return response.data
  })

  const { data: meetings, isLoading: loadingMeetings } = useQuery('dashboard-meetings', async () => {
    const response = await api.get('/api/v1/meetings/', { params: { limit: 5 } })
    return response.data
  })

  const { data: actionItems, isLoading: loadingActions } = useQuery('dashboard-actions', async () => {
    const response = await api.get('/api/v1/action-items/', { params: { limit: 5 } })
    return response.data
  })

  const stats = [
    {
      name: 'Meetings This Week',
      value: analytics?.meeting_stats?.this_week_count ?? 0,
      icon: Calendar,
      color: 'bg-blue-500',
      bg: 'bg-blue-50',
    },
    {
      name: 'Time Saved',
      value: `${analytics?.time_saved_hours ?? 0}h`,
      icon: Clock,
      color: 'bg-emerald-500',
      bg: 'bg-emerald-50',
    },
    {
      name: 'Action Completion',
      value: `${analytics?.action_item_stats?.completion_rate ?? 0}%`,
      icon: CheckCircle,
      color: 'bg-violet-500',
      bg: 'bg-violet-50',
    },
    {
      name: 'Decision Velocity',
      value: `${analytics?.decision_velocity ?? 0}/hr`,
      icon: TrendingUp,
      color: 'bg-orange-500',
      bg: 'bg-orange-50',
    },
  ]

  const recentMeetings: any[] = meetings || []
  const urgentActions = ((actionItems || []) as any[])
    .filter((item) => item.status !== 'completed')
    .slice(0, 4)

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Here's what's happening with your meetings.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loadingAnalytics
          ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          : stats.map((stat) => (
              <div key={stat.name} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{stat.name}</p>
                  <div className={`${stat.bg} rounded-lg p-2`}>
                    <stat.icon className={`w-4 h-4 ${stat.color.replace('bg-', 'text-')}`} />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
            ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Meetings */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">Recent Meetings</h2>
            <Link to="/meetings" className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {loadingMeetings ? (
            <div className="divide-y divide-gray-50">
              {Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)}
            </div>
          ) : recentMeetings.length === 0 ? (
            <EmptyState
              icon={Calendar}
              title="No meetings yet"
              description="Create your first meeting to get started"
              action={
                <Link to="/meetings" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                  Go to Meetings →
                </Link>
              }
            />
          ) : (
            <div className="divide-y divide-gray-50">
              {recentMeetings.map((meeting: any) => (
                <Link
                  key={meeting.id}
                  to={`/meetings/${meeting.id}`}
                  className="flex items-center gap-4 px-6 py-3.5 hover:bg-gray-50 transition-colors group"
                >
                  <div className="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-4 h-4 text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate group-hover:text-primary-700 transition-colors">
                      {meeting.title}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(meeting.scheduled_start).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', year: 'numeric',
                      })} · {meeting.platform}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium flex-shrink-0 ${statusColors[meeting.status] || statusColors.scheduled}`}>
                    {meeting.status?.replace('_', ' ')}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Urgent Action Items */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">Urgent Actions</h2>
            <Link to="/action-items" className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {loadingActions ? (
            <div className="divide-y divide-gray-50">
              {Array.from({ length: 3 }).map((_, i) => <SkeletonRow key={i} />)}
            </div>
          ) : urgentActions.length === 0 ? (
            <EmptyState
              icon={CheckCircle}
              title="All caught up!"
              description="No pending action items right now"
            />
          ) : (
            <div className="divide-y divide-gray-50">
              {urgentActions.map((action: any) => (
                <div key={action.id} className="flex items-start gap-3 px-5 py-3.5">
                  <AlertCircle
                    className={`w-4 h-4 mt-0.5 flex-shrink-0 ${priorityColors[action.priority] || priorityColors.medium}`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 leading-tight">{action.title}</p>
                    <p className="mt-0.5 text-xs text-gray-400">
                      {action.due_date
                        ? `Due ${new Date(action.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
                        : 'No due date'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
