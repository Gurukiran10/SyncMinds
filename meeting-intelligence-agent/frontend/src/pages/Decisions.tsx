import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Vote, CheckCircle, Clock, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '../lib/api'
import { format } from 'date-fns'

interface Decision {
  decision_index: number
  meeting_id: string
  meeting_title: string
  meeting_date: string
  decision: string
  made_by?: string
  timestamp?: string
  actual_outcome?: string
  implementation_status?: string
  outcome_met_expectation?: boolean
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  implemented: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const Decisions: React.FC = () => {
  const qc = useQueryClient()
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [outcomeText, setOutcomeText] = useState('')
  const [outcomeStatus, setOutcomeStatus] = useState('implemented')

  const { data, isLoading } = useQuery('decisions-pending', () =>
    api.get('/api/v1/decisions/pending').then(r => r.data)
  )

  const updateMutation = useMutation(
    ({ meetingId, index, payload }: { meetingId: string; index: number; payload: object }) =>
      api.patch(`/api/v1/meetings/${meetingId}/decisions/${index}`, payload),
    { onSuccess: () => { qc.invalidateQueries('decisions-pending'); setEditingId(null) } }
  )

  const decisions: Decision[] = data?.decisions || []

  const toggleExpand = (id: string) => setExpandedId(expandedId === id ? null : id)

  const startEdit = (d: Decision) => {
    setEditingId(`${d.meeting_id}-${d.decision_index}`)
    setOutcomeText(d.actual_outcome || '')
    setOutcomeStatus(d.implementation_status || 'implemented')
  }

  const saveOutcome = (d: Decision) => {
    updateMutation.mutate({
      meetingId: d.meeting_id,
      index: d.decision_index,
      payload: { actual_outcome: outcomeText, implementation_status: outcomeStatus },
    })
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Vote className="w-8 h-8 text-indigo-600" /> Decisions
        </h1>
        <p className="text-gray-500 mt-1">Track outcomes of decisions made in meetings</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div className="text-3xl font-bold text-yellow-500">{decisions.filter(d => !d.implementation_status || d.implementation_status === 'pending').length}</div>
          <div className="text-sm text-gray-500 mt-1">Pending</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div className="text-3xl font-bold text-blue-500">{decisions.filter(d => d.implementation_status === 'in_progress').length}</div>
          <div className="text-sm text-gray-500 mt-1">In Progress</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div className="text-3xl font-bold text-green-500">{decisions.filter(d => d.implementation_status === 'implemented').length}</div>
          <div className="text-sm text-gray-500 mt-1">Implemented</div>
        </div>
      </div>

      {decisions.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
          <p className="text-gray-500">All decisions have been tracked. Great work!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {decisions.map((d) => {
            const uid = `${d.meeting_id}-${d.decision_index}`
            const isExpanded = expandedId === uid
            const isEditing = editingId === uid
            const status = d.implementation_status || 'pending'

            return (
              <div key={uid} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div
                  className="flex items-start gap-4 p-5 cursor-pointer hover:bg-gray-50"
                  onClick={() => toggleExpand(uid)}
                >
                  <div className="mt-0.5">
                    {status === 'implemented' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : status === 'in_progress' ? (
                      <Clock className="w-5 h-5 text-blue-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900">{d.decision}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-sm text-gray-500">{d.meeting_title}</span>
                      {d.meeting_date && (
                        <span className="text-xs text-gray-400">
                          {format(new Date(d.meeting_date), 'MMM d, yyyy')}
                        </span>
                      )}
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[status] || statusColors.pending}`}>
                        {status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400 mt-1" /> : <ChevronDown className="w-4 h-4 text-gray-400 mt-1" />}
                </div>

                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-gray-100 pt-4">
                    {d.actual_outcome && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-700 mb-1">Outcome recorded:</p>
                        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{d.actual_outcome}</p>
                      </div>
                    )}

                    {isEditing ? (
                      <div className="space-y-3">
                        <textarea
                          className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                          rows={3}
                          placeholder="What actually happened with this decision?"
                          value={outcomeText}
                          onChange={e => setOutcomeText(e.target.value)}
                        />
                        <select
                          className="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                          value={outcomeStatus}
                          onChange={e => setOutcomeStatus(e.target.value)}
                        >
                          <option value="pending">Pending</option>
                          <option value="in_progress">In Progress</option>
                          <option value="implemented">Implemented</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                        <div className="flex gap-2">
                          <button
                            onClick={() => saveOutcome(d)}
                            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => startEdit(d)}
                        className="px-4 py-2 bg-indigo-50 text-indigo-700 text-sm rounded-lg hover:bg-indigo-100"
                      >
                        Record outcome
                      </button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default Decisions
