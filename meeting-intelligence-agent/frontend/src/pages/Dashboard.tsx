import React from 'react'
import { useQuery } from 'react-query'
import { Calendar, Clock, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../lib/api'

const Dashboard: React.FC = () => {
  const { data: analytics } = useQuery('analytics', async () => {
    const response = await api.get('/api/v1/analytics/dashboard')
    return response.data
  })

  const { data: meetings } = useQuery('dashboard-meetings', async () => {
    const response = await api.get('/api/v1/meetings/', { params: { limit: 5 } })
    return response.data
  })

  const { data: actionItems } = useQuery('dashboard-actions', async () => {
    const response = await api.get('/api/v1/action-items/', { params: { limit: 5 } })
    return response.data
  })

  const stats = [
    {
      name: 'Meetings This Week',
      value: analytics?.meeting_stats?.this_week_count ?? 0,
      icon: Calendar,
      color: 'bg-blue-500',
      change: null,
    },
    {
      name: 'Time Saved',
      value: `${analytics?.time_saved_hours ?? 0}h`,
      icon: Clock,
      color: 'bg-green-500',
      change: null,
    },
    {
      name: 'Action Completion',
      value: `${analytics?.action_item_stats?.completion_rate ?? 0}%`,
      icon: CheckCircle,
      color: 'bg-purple-500',
      change: null,
    },
    {
      name: 'Decision Velocity',
      value: `${analytics?.decision_velocity ?? 0}/hr`,
      icon: TrendingUp,
      color: 'bg-orange-500',
      change: null,
    },
  ]

  const recentMeetings = meetings || []
  const urgentActions = (actionItems || []).filter((item: any) => item.status !== 'completed').slice(0, 3)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back! Here's what's happening with your meetings.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                {stat.change && (
                  <p className="mt-2 text-sm text-green-600 font-medium">
                    {stat.change} from last week
                  </p>
                )}
              </div>
              <div className={`${stat.color} rounded-lg p-3`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Meetings */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Meetings</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {recentMeetings.map((meeting: any) => (
              <div key={meeting.id} className="px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900">{meeting.title}</h3>
                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                      <span>{new Date(meeting.scheduled_start).toLocaleString()}</span>
                      <span>•</span>
                      <span>{meeting.platform}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2 text-xs">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                      {meeting.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Urgent Action Items */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Urgent Actions</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {urgentActions.map((action: any, idx: number) => (
              <div key={idx} className="px-6 py-4">
                <div className="flex items-start space-x-3">
                  <AlertCircle
                    className={`w-5 h-5 flex-shrink-0 ${
                      action.priority === 'high' ? 'text-red-500' : 'text-orange-500'
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{action.title}</p>
                    <p className="mt-1 text-xs text-gray-500">Priority: {action.priority}</p>
                    <p className="mt-1 text-xs font-medium text-red-600">Due: {action.due_date ? new Date(action.due_date).toLocaleDateString() : 'No due date'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
