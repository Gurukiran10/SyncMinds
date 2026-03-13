import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { Bell, CheckCircle2, Filter } from 'lucide-react'
import { api } from '../lib/api'
import { SkeletonList } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const sentimentColors: Record<string, string> = {
  positive: 'bg-green-100 text-green-700',
  negative: 'bg-red-100 text-red-700',
  neutral: 'bg-gray-100 text-gray-500',
}

const mentionTypeColors: Record<string, string> = {
  person: 'bg-blue-100 text-blue-700',
  company: 'bg-purple-100 text-purple-700',
  product: 'bg-orange-100 text-orange-700',
  topic: 'bg-teal-100 text-teal-700',
}

const Mentions: React.FC = () => {
  const [unreadOnly, setUnreadOnly] = useState(false)

  const { data: mentions, refetch, isLoading } = useQuery(['mentions', unreadOnly], async () => {
    const response = await api.get('/api/v1/mentions/', { params: { unread_only: unreadOnly } })
    return response.data
  })

  const markRead = async (mentionId: string) => {
    await api.post(`/api/v1/mentions/${mentionId}/read`)
    refetch()
  }

  const unreadCount = (mentions || []).filter((m: any) => !m.notification_read).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mentions</h1>
          <p className="mt-1 text-sm text-gray-500">Track where you were mentioned in meetings.</p>
        </div>
        <button
          onClick={() => setUnreadOnly((v) => !v)}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border transition-colors ${
            unreadOnly
              ? 'bg-primary-50 border-primary-200 text-primary-700'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
          }`}
        >
          <Filter className="w-4 h-4" />
          {unreadOnly ? 'Unread only' : 'All mentions'}
          {!unreadOnly && unreadCount > 0 && (
            <span className="bg-primary-600 text-white text-xs font-semibold px-1.5 py-0.5 rounded-full">
              {unreadCount}
            </span>
          )}
        </button>
      </div>

      {/* Summary */}
      {!isLoading && (mentions || []).length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs text-gray-500 mb-1">Total</p>
            <p className="text-2xl font-bold text-gray-900">{(mentions || []).length}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs text-gray-500 mb-1">Unread</p>
            <p className="text-2xl font-bold text-primary-600">{unreadCount}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs text-gray-500 mb-1">Positive</p>
            <p className="text-2xl font-bold text-green-600">
              {(mentions || []).filter((m: any) => m.sentiment === 'positive').length}
            </p>
          </div>
        </div>
      )}

      {/* List */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <SkeletonList rows={4} />
        ) : (mentions || []).length === 0 ? (
          <EmptyState
            icon={Bell}
            title={unreadOnly ? 'No unread mentions' : 'No mentions yet'}
            description={unreadOnly ? 'All caught up! Switch to "All mentions" to see history.' : 'Mentions are extracted automatically when meetings are analyzed.'}
            action={unreadOnly ? (
              <button onClick={() => setUnreadOnly(false)} className="text-sm font-medium text-primary-600 hover:text-primary-700">
                Show all mentions
              </button>
            ) : undefined}
          />
        ) : (
          <div className="divide-y divide-gray-50">
            {(mentions as any[]).map((mention) => (
              <div
                key={mention.id}
                className={`flex items-start gap-4 px-6 py-4 transition-colors ${
                  !mention.notification_read ? 'bg-primary-50/30' : 'hover:bg-gray-50'
                }`}
              >
                {/* Unread dot / icon */}
                <div className="flex-shrink-0 mt-0.5">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    mention.notification_read ? 'bg-gray-100' : 'bg-primary-100'
                  }`}>
                    <Bell className={`w-4 h-4 ${mention.notification_read ? 'text-gray-400' : 'text-primary-600'}`} />
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium leading-snug ${mention.notification_read ? 'text-gray-700' : 'text-gray-900'}`}>
                    {mention.mentioned_text}
                  </p>
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    {mention.mention_type && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${mentionTypeColors[mention.mention_type] || mentionTypeColors.topic}`}>
                        {mention.mention_type}
                      </span>
                    )}
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sentimentColors[mention.sentiment] || sentimentColors.neutral}`}>
                      {mention.sentiment || 'neutral'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(mention.created_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>

                {/* Mark read */}
                {!mention.notification_read && (
                  <button
                    onClick={() => markRead(mention.id)}
                    className="flex-shrink-0 flex items-center gap-1.5 text-xs font-medium text-primary-600 hover:text-primary-700 px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Mark read
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Mentions
