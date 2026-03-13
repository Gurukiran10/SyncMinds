import React from 'react'
import { useQuery } from 'react-query'
import { api } from '../lib/api'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  scheduled: 'bg-gray-100 text-gray-700',
  transcribing: 'bg-blue-100 text-blue-700',
  failed: 'bg-red-100 text-red-700',
}

const Analytics: React.FC = () => {
  const { data: dashboard } = useQuery('analytics-dashboard', async () => {
    const response = await api.get('/api/v1/analytics/dashboard')
    return response.data
  })

  const { data: efficiency } = useQuery('meeting-efficiency', async () => {
    const response = await api.get('/api/v1/analytics/meeting-efficiency')
    return response.data
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-2 text-gray-600">Measure meeting efficiency and execution quality.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Total Meetings</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{dashboard?.meeting_stats?.total_meetings ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Total Hours</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{dashboard?.meeting_stats?.total_hours ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Action Completion</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{dashboard?.action_item_stats?.completion_rate ?? 0}%</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Decision Velocity</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{dashboard?.decision_velocity ?? 0}/hr</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900">Meeting Efficiency</h2>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Avg Decisions Per Hour</p>
            <p className="font-semibold text-gray-900">{efficiency?.avg_decisions_per_hour ?? 0}</p>
          </div>
          <div>
            <p className="text-gray-500">Avg Action Items Per Hour</p>
            <p className="font-semibold text-gray-900">{efficiency?.avg_action_items_per_hour ?? 0}</p>
          </div>
          <div>
            <p className="text-gray-500">Execution Completion</p>
            <p className="font-semibold text-gray-900">{efficiency?.completion_ratio ?? 0}%</p>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Sentiment Trend</h3>
          <div className="flex items-end gap-3 h-28">
            {(efficiency?.sentiment_trend || []).map((point: any, index: number) => {
              const normalized = Number(point?.score ?? 0)
              const height = Math.max(12, ((normalized + 1) / 2) * 100)
              return (
                <div key={index} className="flex flex-col items-center gap-2">
                  <div
                    className="bg-primary-600 rounded-t w-8"
                    style={{ height: `${height}%` }}
                    title={`${point?.label}: ${normalized}`}
                  />
                  <span className="text-xs text-gray-500">{point?.label}</span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Status Breakdown</h3>
            <div className="space-y-2">
              {Object.entries(efficiency?.status_breakdown || {}).length ? (
                Object.entries(efficiency?.status_breakdown || {}).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2">
                    <span className="text-sm text-gray-700 capitalize">{status.replace('_', ' ')}</span>
                    <span className="text-sm font-semibold text-gray-900">{String(count)}</span>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">No status data yet.</div>
              )}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Meetings</h3>
            <div className="space-y-3">
              {(efficiency?.recent_meetings || []).length ? (
                efficiency.recent_meetings.map((meeting: any) => (
                  <div key={meeting.id} className="rounded-lg border border-gray-200 p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-gray-900">{meeting.title}</p>
                        <p className="mt-1 text-xs text-gray-500">{new Date(meeting.scheduled_start).toLocaleString()}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs ${statusColors[meeting.status] || 'bg-gray-100 text-gray-700'}`}>
                        {meeting.status}
                      </span>
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-gray-600">
                      <div>
                        <p>Duration</p>
                        <p className="font-semibold text-gray-900">{meeting.duration_minutes} min</p>
                      </div>
                      <div>
                        <p>Actions</p>
                        <p className="font-semibold text-gray-900">{meeting.action_items_count}</p>
                      </div>
                      <div>
                        <p>Decisions</p>
                        <p className="font-semibold text-gray-900">{meeting.decisions_count}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">No meeting insights yet.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
