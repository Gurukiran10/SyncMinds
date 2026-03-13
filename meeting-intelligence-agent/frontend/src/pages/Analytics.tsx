import React from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { BarChart3, Clock, CheckCircle, Zap, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'
import { SkeletonCard, Skeleton } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  scheduled: 'bg-gray-100 text-gray-600',
  transcribing: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-blue-100 text-blue-700',
  failed: 'bg-red-100 text-red-700',
}

const Analytics: React.FC = () => {
  const { data: dashboard, isLoading: loadingDashboard } = useQuery('analytics-dashboard', async () => {
    const response = await api.get('/api/v1/analytics/dashboard')
    return response.data
  })

  const { data: efficiency, isLoading: loadingEfficiency } = useQuery('meeting-efficiency', async () => {
    const response = await api.get('/api/v1/analytics/meeting-efficiency')
    return response.data
  })

  const stats = [
    {
      label: 'Total Meetings',
      value: dashboard?.meeting_stats?.total_meetings ?? 0,
      icon: BarChart3,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-500',
    },
    {
      label: 'Total Hours',
      value: `${dashboard?.meeting_stats?.total_hours ?? 0}h`,
      icon: Clock,
      iconBg: 'bg-purple-50',
      iconColor: 'text-purple-500',
    },
    {
      label: 'Action Completion',
      value: `${dashboard?.action_item_stats?.completion_rate ?? 0}%`,
      icon: CheckCircle,
      iconBg: 'bg-green-50',
      iconColor: 'text-green-500',
    },
    {
      label: 'Decision Velocity',
      value: `${dashboard?.decision_velocity ?? 0}/hr`,
      icon: Zap,
      iconBg: 'bg-orange-50',
      iconColor: 'text-orange-500',
    },
  ]

  const sentimentTrend: any[] = efficiency?.sentiment_trend || []
  const maxSentiment = Math.max(...sentimentTrend.map((p: any) => Math.abs(Number(p?.score ?? 0))), 1)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">Measure meeting efficiency and execution quality.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loadingDashboard
          ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          : stats.map((stat) => (
              <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{stat.label}</p>
                  <div className={`${stat.iconBg} rounded-lg p-2`}>
                    <stat.icon className={`w-4 h-4 ${stat.iconColor}`} />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
            ))}
      </div>

      {loadingEfficiency ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 space-y-3">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-8 w-1/4" />
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Efficiency metrics */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Meeting Efficiency</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                { label: 'Avg Decisions / Hour', value: efficiency?.avg_decisions_per_hour ?? 0 },
                { label: 'Avg Action Items / Hour', value: efficiency?.avg_action_items_per_hour ?? 0 },
                { label: 'Execution Completion', value: `${efficiency?.completion_ratio ?? 0}%` },
              ].map(({ label, value }) => (
                <div key={label} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <p className="text-xs text-gray-500 mb-1">{label}</p>
                  <p className="text-2xl font-bold text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sentiment trend */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-4">Sentiment Trend</h2>
              {sentimentTrend.length === 0 ? (
                <EmptyState icon={BarChart3} title="No sentiment data yet" description="Sentiment is extracted after meeting analysis" />
              ) : (
                <div className="flex items-end gap-2 h-36 mt-2">
                  {sentimentTrend.map((point: any, i: number) => {
                    const score = Number(point?.score ?? 0)
                    const isPositive = score >= 0
                    const heightPct = Math.max(8, (Math.abs(score) / maxSentiment) * 90)
                    return (
                      <div key={i} className="flex flex-col items-center gap-1.5 flex-1 min-w-0">
                        <div className="w-full flex flex-col justify-end" style={{ height: '120px' }}>
                          <div
                            className={`w-full rounded-t-md transition-all ${isPositive ? 'bg-green-400' : 'bg-red-400'}`}
                            style={{ height: `${heightPct}%` }}
                            title={`${point?.label}: ${score.toFixed(2)}`}
                          />
                        </div>
                        <span className="text-xs text-gray-400 truncate w-full text-center">{point?.label}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Status breakdown */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-900 mb-4">Status Breakdown</h2>
              {Object.entries(efficiency?.status_breakdown || {}).length === 0 ? (
                <EmptyState icon={BarChart3} title="No data yet" description="Data appears after meetings are created" />
              ) : (
                <div className="space-y-2">
                  {Object.entries(efficiency?.status_breakdown || {}).map(([status, count]) => {
                    const total = Object.values(efficiency?.status_breakdown || {}).reduce((a: number, b) => a + Number(b), 0)
                    const pct = total > 0 ? Math.round((Number(count) / total) * 100) : 0
                    return (
                      <div key={status}>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[status] || statusColors.scheduled}`}>
                              {status.replace('_', ' ')}
                            </span>
                          </div>
                          <span className="text-sm font-semibold text-gray-900">{String(count)}</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-400 rounded-full transition-all"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Recent meetings */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 className="text-sm font-semibold text-gray-900">Recent Meeting Insights</h2>
              <Link to="/meetings" className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium">
                View all <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            {(efficiency?.recent_meetings || []).length === 0 ? (
              <EmptyState icon={BarChart3} title="No meeting insights yet" description="Insights appear after meetings are transcribed and analyzed" />
            ) : (
              <div className="divide-y divide-gray-50">
                {efficiency.recent_meetings.map((meeting: any) => (
                  <Link
                    key={meeting.id}
                    to={`/meetings/${meeting.id}`}
                    className="flex items-center gap-5 px-6 py-4 hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 group-hover:text-primary-700 truncate">{meeting.title}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {new Date(meeting.scheduled_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </p>
                    </div>
                    <div className="flex items-center gap-4 flex-shrink-0">
                      <div className="text-center">
                        <p className="text-sm font-semibold text-gray-900">{meeting.duration_minutes}</p>
                        <p className="text-xs text-gray-400">min</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-semibold text-gray-900">{meeting.action_items_count}</p>
                        <p className="text-xs text-gray-400">actions</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-semibold text-gray-900">{meeting.decisions_count}</p>
                        <p className="text-xs text-gray-400">decisions</p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColors[meeting.status] || statusColors.scheduled}`}>
                        {meeting.status}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default Analytics
