import React, { useMemo, useState } from 'react'
import { useQuery } from 'react-query'
import { CheckCircle, Circle, Clock, Search, X, CheckSquare, Plus } from 'lucide-react'
import { api } from '../lib/api'
import { SkeletonList } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
}

const ActionItems: React.FC = () => {
  const [error, setError] = useState('')
  const [banner, setBanner] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '',
    description: '',
    meeting_id: '',
    priority: 'medium',
    due_date: '',
  })

  const { data: actionItems, isLoading, refetch } = useQuery('action-items', async () => {
    const response = await api.get('/api/v1/action-items/')
    return response.data
  })

  const { data: meetings } = useQuery('meetings-for-actions', async () => {
    const response = await api.get('/api/v1/meetings/')
    return response.data
  })

  const items: any[] = actionItems || []
  const now = new Date()

  const meetingTitle = (meetingId: string) => {
    const meeting = (meetings || []).find((m: any) => m.id === meetingId)
    return meeting?.title || 'Unknown meeting'
  }

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch = !search.trim() || [item.title, item.description, meetingTitle(item.meeting_id)]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(search.toLowerCase()))
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter
      const matchesPriority = priorityFilter === 'all' || item.priority === priorityFilter
      return matchesSearch && matchesStatus && matchesPriority
    })
  }, [items, search, statusFilter, priorityFilter, meetings])

  const overdueCount = filteredItems.filter((item) =>
    item.due_date && new Date(item.due_date) < now && item.status !== 'completed'
  ).length

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setBanner(null)
    try {
      await api.post('/api/v1/action-items/', {
        title: form.title.trim(),
        description: form.description.trim(),
        meeting_id: form.meeting_id,
        due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
        priority: form.priority,
      })
      setForm({ title: '', description: '', meeting_id: '', priority: 'medium', due_date: '' })
      setShowCreate(false)
      setBanner({ type: 'success', message: 'Action item created successfully.' })
      refetch()
    } catch (err: any) {
      const message = err?.response?.data?.detail || 'Failed to create action item'
      setError(message)
      setBanner({ type: 'error', message })
    }
  }

  const handleMarkComplete = async (id: string) => {
    try {
      await api.post(`/api/v1/action-items/${id}/complete`)
      setBanner({ type: 'success', message: 'Marked as complete.' })
      refetch()
    } catch (err: any) {
      setBanner({ type: 'error', message: err?.response?.data?.detail || 'Failed to update.' })
    }
  }

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.patch(`/api/v1/action-items/${id}`, { status })
      refetch()
    } catch (err: any) {
      setBanner({ type: 'error', message: err?.response?.data?.detail || 'Failed to update status.' })
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'in_progress': return <Clock className="w-5 h-5 text-blue-500" />
      default: return <Circle className="w-5 h-5 text-gray-300" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Action Items</h1>
          <p className="mt-1 text-sm text-gray-500">Track and manage your meeting action items.</p>
        </div>
        <button
          onClick={() => setShowCreate((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors flex-shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">New Item</span>
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
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">New Action Item</h2>
            <button onClick={() => setShowCreate(false)} className="p-1 rounded text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          </div>
          <form onSubmit={handleCreate} className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Title *</label>
              <input
                required
                placeholder="What needs to be done?"
                value={form.title}
                onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Description</label>
              <input
                placeholder="Optional details"
                value={form.description}
                onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Meeting *</label>
              <select
                required
                value={form.meeting_id}
                onChange={(e) => setForm((prev) => ({ ...prev, meeting_id: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              >
                <option value="">Select meeting</option>
                {(meetings || []).map((meeting: any) => (
                  <option key={meeting.id} value={meeting.id}>{meeting.title}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Due Date</label>
              <input
                type="date"
                value={form.due_date}
                onChange={(e) => setForm((prev) => ({ ...prev, due_date: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Priority</label>
              <select
                value={form.priority}
                onChange={(e) => setForm((prev) => ({ ...prev, priority: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
            <div className="sm:col-span-2 flex justify-end gap-2 pt-1">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                Create Item
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total', value: filteredItems.length, color: 'text-gray-900' },
          { label: 'In Progress', value: filteredItems.filter((i) => i.status === 'in_progress').length, color: 'text-blue-600' },
          { label: 'Completed', value: filteredItems.filter((i) => i.status === 'completed').length, color: 'text-green-600' },
          { label: 'Overdue', value: overdueCount, color: 'text-red-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            placeholder="Search action items..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
        >
          <option value="all">All statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="blocked">Blocked</option>
          <option value="completed">Completed</option>
        </select>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
        >
          <option value="all">All priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      {/* List */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <SkeletonList rows={5} />
        ) : filteredItems.length ? (
          <div className="divide-y divide-gray-50">
            {filteredItems.map((item: any) => {
              const isOverdue = item.due_date && new Date(item.due_date) < now && item.status !== 'completed'
              return (
                <div key={item.id} className="flex items-start gap-4 px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="mt-0.5 flex-shrink-0">{getStatusIcon(item.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 flex-wrap">
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${item.status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
                          {item.title}
                        </p>
                        {item.description && (
                          <p className="text-xs text-gray-400 mt-0.5 truncate">{item.description}</p>
                        )}
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1.5 text-xs text-gray-400">
                          <span className="truncate max-w-[200px]">{meetingTitle(item.meeting_id)}</span>
                          {item.due_date && (
                            <span className={isOverdue ? 'text-red-500 font-medium' : ''}>
                              Due {new Date(item.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                              {isOverdue ? ' · Overdue' : ''}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priorityColors[item.priority] || priorityColors.low}`}>
                          {item.priority}
                        </span>
                        <select
                          value={item.status}
                          onChange={(e) => handleStatusChange(item.id, e.target.value)}
                          className="text-xs px-2 py-1 border border-gray-200 rounded-lg bg-white focus:ring-1 focus:ring-primary-500 focus:outline-none"
                        >
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="blocked">Blocked</option>
                          <option value="completed">Completed</option>
                        </select>
                        {item.status !== 'completed' && (
                          <button
                            onClick={() => handleMarkComplete(item.id)}
                            className="text-xs text-primary-600 hover:text-primary-700 font-medium whitespace-nowrap"
                          >
                            ✓ Done
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <EmptyState
            icon={CheckSquare}
            title={search || statusFilter !== 'all' || priorityFilter !== 'all' ? 'No items match your filters' : 'No action items yet'}
            description={search || statusFilter !== 'all' || priorityFilter !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Action items will be automatically extracted from your meeting recordings'}
            action={search || statusFilter !== 'all' || priorityFilter !== 'all' ? (
              <button
                onClick={() => { setSearch(''); setStatusFilter('all'); setPriorityFilter('all') }}
                className="text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                Clear filters
              </button>
            ) : undefined}
          />
        )}
      </div>
    </div>
  )
}

export default ActionItems
