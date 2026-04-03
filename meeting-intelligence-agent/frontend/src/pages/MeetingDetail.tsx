import React, { useMemo, useState } from 'react'
import { useQuery } from 'react-query'
import { Link, useParams } from 'react-router-dom'
import {
  UploadCloud, ArrowLeft, CheckSquare, MessageSquare,
  Lightbulb, Hash, Loader2, AlertCircle,
} from 'lucide-react'
import { api } from '../lib/api'
import { Skeleton, SkeletonText } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  in_progress: 'bg-blue-100 text-blue-700',
  scheduled: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-700',
}

const impactColors: Record<string, string> = {
  high: 'bg-red-50 text-red-700 border-red-100',
  medium: 'bg-yellow-50 text-yellow-700 border-yellow-100',
  low: 'bg-gray-50 text-gray-600 border-gray-100',
}

const MeetingDetail: React.FC = () => {
  const { id } = useParams()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const { data: meeting, isLoading, refetch } = useQuery(
    ['meeting', id],
    async () => {
      const response = await api.get(`/api/v1/meetings/${id}`)
      return response.data
    },
    {
      refetchInterval: (data: any) => {
        if (!data) return false
        const s = String(data.status || '').toLowerCase()
        const t = String(data.transcription_status || '').toLowerCase()
        const a = String(data.analysis_status || '').toLowerCase()
        const isProcessing =
          ['transcribing', 'processing', 'in_progress'].includes(s) ||
          t === 'processing' || a === 'processing'
        return isProcessing ? 2500 : false
      },
    },
  )

  const { data: allActionItems } = useQuery(
    ['meeting-action-items', id],
    async () => {
      const response = await api.get('/api/v1/action-items/')
      return response.data
    },
    { enabled: Boolean(id) },
  )

  const { data: allMentions } = useQuery(
    ['meeting-mentions', id],
    async () => {
      const response = await api.get('/api/v1/mentions/')
      return response.data
    },
    { enabled: Boolean(id) },
  )

  const meetingActionItems = useMemo(
    () => (allActionItems || []).filter((item: any) => item.meeting_id === id),
    [allActionItems, id],
  )

  const meetingMentions = useMemo(
    () => (allMentions || []).filter((mention: any) => mention.meeting_id === id),
    [allMentions, id],
  )

  const decisions = Array.isArray(meeting?.key_decisions) ? meeting.key_decisions : []
  const topics = Array.isArray(meeting?.discussion_topics) ? meeting.discussion_topics : []

  const processingState = useMemo(() => {
    if (!meeting) return null
    const s = String(meeting.status || '').toLowerCase()
    const t = String(meeting.transcription_status || '').toLowerCase()
    const a = String(meeting.analysis_status || '').toLowerCase()
    if (t === 'processing' || s === 'transcribing') return { text: 'Transcribing recording...', type: 'processing' }
    if (a === 'processing' || s === 'processing' || s === 'in_progress') return { text: 'Analyzing with AI...', type: 'processing' }
    if (s === 'failed' || t === 'failed' || a === 'failed') return { text: 'Processing failed. Please upload again.', type: 'error' }
    return null
  }, [meeting])

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !id) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      setIsUploading(true)
      setUploadMessage(null)
      await api.post(`/api/v1/meetings/${id}/upload`, formData, { timeout: 30000 })
      setUploadMessage({ type: 'success', text: 'Upload successful. Processing started.' })
      await refetch()
    } catch (err: any) {
      setUploadMessage({ type: 'error', text: err?.response?.data?.detail || 'Upload failed. Please try again.' })
    } finally {
      setIsUploading(false)
      event.target.value = ''
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl">
        <Skeleton className="h-8 w-48" />
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <Skeleton className="h-7 w-2/3" />
          <SkeletonText lines={2} />
          <div className="grid grid-cols-2 gap-4 pt-2">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12 rounded-lg" />)}
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 space-y-3">
              <Skeleton className="h-5 w-1/3" />
              <SkeletonText lines={3} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!meeting) {
    return (
      <div className="max-w-5xl">
        <EmptyState
          icon={AlertCircle}
          title="Meeting not found"
          description="This meeting may have been deleted or you may not have access"
          action={<Link to="/meetings" className="text-sm font-medium text-primary-600 hover:text-primary-700">← Back to Meetings</Link>}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Back link */}
      <Link to="/meetings" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to Meetings
      </Link>

      {/* Meeting header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-gray-900">{meeting.title}</h1>
            {meeting.description && (
              <p className="mt-1 text-sm text-gray-500">{meeting.description}</p>
            )}
          </div>
          <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex-shrink-0 ${statusColors[meeting.status] || statusColors.scheduled}`}>
            {meeting.status?.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Platform', value: meeting.platform },
            { label: 'Type', value: meeting.meeting_type || 'internal' },
            { label: 'Start', value: new Date(meeting.scheduled_start).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) },
            { label: 'End', value: new Date(meeting.scheduled_end).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) },
          ].map(({ label, value }) => (
            <div key={label} className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-0.5">{label}</p>
              <p className="text-sm font-medium text-gray-800 capitalize">{value}</p>
            </div>
          ))}
        </div>

        {/* Processing state */}
        {processingState && (
          <div className={`mt-4 flex items-center gap-2.5 px-4 py-3 rounded-lg text-sm ${
            processingState.type === 'error' ? 'bg-red-50 text-red-700 border border-red-100' : 'bg-blue-50 text-blue-700 border border-blue-100'
          }`}>
            {processingState.type === 'processing'
              ? <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
              : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
            {processingState.text}
          </div>
        )}
      </div>

      {/* Upload */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-1">Upload Recording</h2>
        <p className="text-xs text-gray-500 mb-4">Upload audio or video to trigger AI transcription and analysis.</p>
        <div className="flex items-center gap-3 flex-wrap">
          <label className={`inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg cursor-pointer transition-colors ${
            isUploading
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}>
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
            {isUploading ? 'Uploading...' : 'Choose File'}
            <input type="file" className="hidden" onChange={handleUpload} disabled={isUploading} accept="audio/*,video/*" />
          </label>
          {uploadMessage && (
            <span className={`text-sm ${uploadMessage.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {uploadMessage.text}
            </span>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-3">AI Summary</h2>
        {meeting.summary ? (
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{meeting.summary}</p>
        ) : (
          <p className="text-sm text-gray-400 italic">Summary will appear after processing.</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Decisions */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-4 h-4 text-yellow-500" />
            <h2 className="text-sm font-semibold text-gray-900">Key Decisions</h2>
            {decisions.length > 0 && (
              <span className="ml-auto text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{decisions.length}</span>
            )}
          </div>
          {decisions.length ? (
            <div className="space-y-3">
              {decisions.map((decision: any, index: number) => (
                <div key={index} className="rounded-lg border border-gray-100 p-4 bg-gray-50">
                  <p className="text-sm font-medium text-gray-900">{decision.decision || `Decision ${index + 1}`}</p>
                  {decision.reasoning && (
                    <p className="mt-1 text-xs text-gray-500 leading-relaxed">{decision.reasoning}</p>
                  )}
                  {decision.impact_level && (
                    <span className={`mt-2 inline-block text-xs px-2 py-0.5 rounded border font-medium ${impactColors[decision.impact_level] || impactColors.low}`}>
                      {decision.impact_level} impact
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 italic">No decisions extracted yet.</p>
          )}
        </div>

        {/* Discussion Topics */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Hash className="w-4 h-4 text-blue-500" />
            <h2 className="text-sm font-semibold text-gray-900">Discussion Topics</h2>
            {topics.length > 0 && (
              <span className="ml-auto text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{topics.length}</span>
            )}
          </div>
          {topics.length ? (
            <div className="flex flex-wrap gap-2">
              {topics.map((topic: string, index: number) => (
                <span key={index} className="px-3 py-1.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-full border border-primary-100">
                  {topic}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 italic">Topics will appear after analysis.</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Action Items */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-green-500" />
              <h2 className="text-sm font-semibold text-gray-900">Action Items</h2>
              {meetingActionItems.length > 0 && (
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{meetingActionItems.length}</span>
              )}
            </div>
            <Link to="/action-items" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all</Link>
          </div>
          {meetingActionItems.length ? (
            <div className="space-y-2.5">
              {meetingActionItems.slice(0, 5).map((item: any) => (
                <div key={item.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border border-gray-100">
                  <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                    item.status === 'completed' ? 'bg-green-500' : item.status === 'in_progress' ? 'bg-blue-500' : 'bg-gray-300'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                    {item.description && <p className="text-xs text-gray-400 mt-0.5 truncate">{item.description}</p>}
                  </div>
                  <span className="text-xs text-gray-400 capitalize flex-shrink-0">{item.status?.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={CheckSquare} title="No action items" description="Action items will be extracted after analysis" />
          )}
        </div>

        {/* Mentions */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-purple-500" />
              <h2 className="text-sm font-semibold text-gray-900">Mentions</h2>
              {meetingMentions.length > 0 && (
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{meetingMentions.length}</span>
              )}
            </div>
            <Link to="/mentions" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all</Link>
          </div>
          {meetingMentions.length ? (
            <div className="space-y-2.5">
              {meetingMentions.slice(0, 5).map((mention: any) => (
                <div key={mention.id} className="p-3 rounded-lg bg-gray-50 border border-gray-100">
                  <p className="text-sm font-medium text-gray-900">{mention.mentioned_text}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-xs text-gray-400 capitalize">{mention.mention_type}</span>
                    <span className="text-gray-200">·</span>
                    <span className={`text-xs ${
                      mention.sentiment === 'positive' ? 'text-green-600' :
                      mention.sentiment === 'negative' ? 'text-red-500' : 'text-gray-400'
                    }`}>{mention.sentiment || 'neutral'}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={MessageSquare} title="No mentions" description="Mentions will be extracted after analysis" />
          )}
        </div>
      </div>
    </div>
  )
}

export default MeetingDetail
