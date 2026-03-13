import React from 'react'
import { useState } from 'react'
import { useQuery } from 'react-query'
import { Bell, CheckCircle2 } from 'lucide-react'
import { api } from '../lib/api'

const Mentions: React.FC = () => {
  const [unreadOnly, setUnreadOnly] = useState(false)

  const { data: mentions, refetch, isLoading } = useQuery(['mentions', unreadOnly], async () => {
    const response = await api.get('/api/v1/mentions/', {
      params: {
        unread_only: unreadOnly,
      },
    })
    return response.data
  })

  const markRead = async (mentionId: string) => {
    await api.post(`/api/v1/mentions/${mentionId}/read`)
    refetch()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mentions</h1>
          <p className="mt-2 text-gray-600">Track where you were mentioned in meetings.</p>
        </div>
        <button
          onClick={() => setUnreadOnly((value) => !value)}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          {unreadOnly ? 'Show All' : 'Unread Only'}
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 divide-y divide-gray-200">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading mentions...</div>
        ) : mentions?.length ? (
          mentions.map((mention: any) => (
            <div key={mention.id} className="p-6 flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Bell className={`w-5 h-5 mt-1 ${mention.notification_read ? 'text-gray-400' : 'text-primary-600'}`} />
                <div>
                  <p className="text-sm font-medium text-gray-900">{mention.mentioned_text}</p>
                  <p className="mt-1 text-xs text-gray-500">Type: {mention.mention_type} • Sentiment: {mention.sentiment || 'neutral'}</p>
                  <p className="mt-1 text-xs text-gray-500">{new Date(mention.created_at).toLocaleString()}</p>
                </div>
              </div>
              {!mention.notification_read && (
                <button
                  onClick={() => markRead(mention.id)}
                  className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
                >
                  <CheckCircle2 className="w-4 h-4" /> Mark read
                </button>
              )}
            </div>
          ))
        ) : (
          <div className="p-10 text-center text-gray-500">No mentions found.</div>
        )}
      </div>
    </div>
  )
}

export default Mentions
