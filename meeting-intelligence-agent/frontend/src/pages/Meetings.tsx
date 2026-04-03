import React, { useEffect, useMemo, useState } from 'react'
import { useQuery } from 'react-query'
import { Plus, Search, Trash2, Calendar, ChevronRight, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { SkeletonList } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  in_progress: 'bg-blue-100 text-blue-700',
  scheduled: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-700',
}

const Meetings: React.FC = () => {
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [createError, setCreateError] = useState('')
  const [banner, setBanner] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [form, setForm] = useState({
    title: '',
    description: '',
    meeting_type: 'internal',
    platform: 'manual',
    scheduled_start: '',
    scheduled_end: '',
  })

  const { data: meetings, isLoading, refetch } = useQuery('meetings', async () => {
    const response = await api.get('/api/v1/meetings/')
    return response.data
  })

  const filteredMeetings = useMemo(() => {
    const list = meetings || []
    if (!search.trim()) return list
    const q = search.toLowerCase()
    return list.filter((meeting: any) =>
      [meeting.title, meeting.description, meeting.platform, meeting.status]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(q)),
    )
  }, [meetings, search])

  useEffect(() => {
    if (!banner) return
    const id = window.setTimeout(() => setBanner(null), 4000)
    return () => window.clearTimeout(id)
  }, [banner])

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault()
    setCreateError('')
    const start = new Date(form.scheduled_start)
    const end = new Date(form.scheduled_end)
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      setCreateError('Please enter valid start and end date/time values.')
      return
    }
    if (end <= start) {
      setCreateError('End time must be after start time.')
      return
    }
    try {
      setIsCreating(true)
      await api.post('/api/v1/meetings/', {
        ...form,
        title: form.title.trim(),
        description: form.description.trim(),
        scheduled_start: start.toISOString(),
        scheduled_end: end.toISOString(),
        attendee_ids: [],
        tags: [],
      }, { timeout: 15000 })
      setShowCreate(false)
      setForm({ title: '', description: '', meeting_type: 'internal', platform: 'manual', scheduled_start: '', scheduled_end: '' })
      setBanner({ type: 'success', message: 'Meeting created successfully.' })
      refetch()
    } catch (err: any) {
      const message = err?.code === 'ECONNABORTED'
        ? 'Request timed out. Please try again.'
        : err?.response?.data?.detail || 'Failed to create meeting.'
      setCreateError(message)
      setBanner({ type: 'error', message })
    } finally {
      setIsCreating(false)
    }
  }

  const handleDelete = async (meetingId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    await api.delete(`/api/v1/meetings/${meetingId}`)
    refetch()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meetings</h1>
          <p className="mt-1 text-sm text-gray-500">View and manage your meeting recordings.</p>
        </div>
        <button
          onClick={() => setShowCreate((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors flex-shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">New Meeting</span>
          <span className="sm:hidden">New</span>
        </button>
      </div>

      {/* Banner */}
      {banner && (
        <div className={`flex items-center justify-between rounded-lg border px-4 py-3 text-sm ${
          banner.type === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'
        }`}>
          <span>{banner.message}</span>
          <button onClick={() => setBanner(null)} className="ml-3 opacity-60 hover:opacity-100">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            required
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          />
          <select
            value={form.platform}
            onChange={(e) => setForm((prev) => ({ ...prev, platform: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="manual">Manual Upload</option>
            <option value="zoom">Zoom</option>
            <option value="google_meet">Google Meet</option>
            <option value="microsoft_teams">Microsoft Teams</option>
          </select>
          <input
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-lg md:col-span-2"
          />
          <div>
            <label className="block text-xs text-gray-500 mb-1">Start Time</label>
            <input
              required
              type="datetime-local"
              value={form.scheduled_start}
              onChange={(e) => setForm((prev) => ({ ...prev, scheduled_start: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-lg w-full"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">End Time</label>
            <input
              required
              type="datetime-local"
              value={form.scheduled_end}
              onChange={(e) => setForm((prev) => ({ ...prev, scheduled_end: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-lg w-full"
            />
          </div>
          <div className="md:col-span-2 flex justify-end gap-2">
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 border border-gray-300 rounded-lg">Cancel</button>
            <button type="submit" disabled={isCreating} className="px-4 py-2 bg-primary-600 text-white rounded-lg disabled:opacity-60 disabled:cursor-not-allowed">
              {isCreating ? 'Creating...' : 'Create'}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">New Meeting</h2>
            <button onClick={() => setShowCreate(false)} className="p-1 rounded text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          </div>
          <form onSubmit={handleCreate} className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Title *</label>
              <input
                required
                placeholder="e.g. Q2 Planning Sync"
                value={form.title}
                onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Description</label>
              <input
                placeholder="Optional description"
                value={form.description}
                onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Start *</label>
              <input
                required
                type="datetime-local"
                value={form.scheduled_start}
                onChange={(e) => setForm((prev) => ({ ...prev, scheduled_start: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">End *</label>
              <input
                required
                type="datetime-local"
                value={form.scheduled_end}
                onChange={(e) => setForm((prev) => ({ ...prev, scheduled_end: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            {createError && (
              <p className="sm:col-span-2 text-sm text-red-600">{createError}</p>
            )}
            <div className="sm:col-span-2 flex justify-end gap-2 pt-1">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" disabled={isCreating} className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-60 disabled:cursor-not-allowed">
                {isCreating ? 'Creating...' : 'Create Meeting'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search meetings..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
        />
        {search && (
          <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Meetings List */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <SkeletonList rows={5} />
        ) : filteredMeetings && filteredMeetings.length > 0 ? (
          <div className="divide-y divide-gray-50">
            {filteredMeetings.map((meeting: any) => (
              <Link
                key={meeting.id}
                to={`/meetings/${meeting.id}`}
                className="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 group-hover:text-primary-700 transition-colors truncate">
                    {meeting.title}
                  </p>
                  {meeting.description && (
                    <p className="text-xs text-gray-400 truncate mt-0.5">{meeting.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-xs text-gray-400">
                      {new Date(meeting.scheduled_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                    <span className="text-gray-200">·</span>
                    <span className="text-xs text-gray-400 capitalize">{meeting.platform}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className={`hidden sm:inline text-xs px-2 py-1 rounded-full font-medium ${statusColors[meeting.status] || statusColors.scheduled}`}>
                    {meeting.status?.replace('_', ' ')}
                  </span>
                  <button
                    onClick={(e) => handleDelete(meeting.id, e)}
                    className="p-1.5 text-gray-300 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100"
                    title="Delete meeting"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-gray-500 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Calendar}
            title={search ? 'No meetings match your search' : 'No meetings yet'}
            description={search ? 'Try different keywords or clear the search' : 'Create your first meeting to start tracking and analyzing your discussions'}
            action={
              search ? (
                <button onClick={() => setSearch('')} className="text-sm font-medium text-primary-600 hover:text-primary-700">
                  Clear search
                </button>
              ) : (
                <button
                  onClick={() => setShowCreate(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Plus className="w-4 h-4" /> Create Meeting
                </button>
              )
            }
          />
        )}
      </div>
    </div>
  )
}

export default Meetings
