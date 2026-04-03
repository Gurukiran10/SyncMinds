import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { Brain, Search, TrendingUp, Network } from 'lucide-react'
import { api } from '../lib/api'

interface SearchResult {
  meeting_id: string
  meeting_title: string
  meeting_date: string
  score: number
  snippet: string
}

interface Topic {
  topic: string
  count: number
  meetings: string[]
}

const Knowledge: React.FC = () => {
  const [query, setQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'search' | 'topics'>('search')

  const { data: searchData, isLoading: searching, refetch: doSearch } = useQuery(
    ['knowledge-search', query],
    () => api.get('/api/v1/knowledge/search', { params: { q: query, limit: 10 } }).then(r => r.data),
    { enabled: false }
  )

  const { data: topicsData, isLoading: loadingTopics } = useQuery(
    'knowledge-topics',
    () => api.get('/api/v1/knowledge/topics').then(r => r.data),
    { enabled: activeTab === 'topics' }
  )

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) doSearch()
  }

  const results: SearchResult[] = searchData?.results || []
  const topics: Topic[] = topicsData?.topics || []

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Brain className="w-8 h-8 text-indigo-600" /> Knowledge Base
        </h1>
        <p className="text-gray-500 mt-1">Search across all meetings and discover recurring topics</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit">
        {[
          { key: 'search', label: 'Semantic Search', icon: Search },
          { key: 'topics', label: 'Recurring Topics', icon: TrendingUp },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as 'search' | 'topics')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === key ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {activeTab === 'search' && (
        <div>
          <form onSubmit={handleSearch} className="flex gap-3 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-sm"
                placeholder="Search meetings... e.g. 'AI accuracy improvements', 'customer feedback'"
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={!query.trim() || searching}
              className="px-6 py-3 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {results.length > 0 && (
            <div className="space-y-3">
              <p className="text-sm text-gray-500">{results.length} results for "{searchData?.query}"</p>
              {results.map((r, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-indigo-200 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{r.meeting_title}</h3>
                      {r.meeting_date && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          {new Date(r.meeting_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </p>
                      )}
                      {r.snippet && (
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">{r.snippet}</p>
                      )}
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-sm font-semibold text-indigo-600">{Math.round(r.score * 100)}%</div>
                      <div className="text-xs text-gray-400">relevance</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {searchData && results.length === 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <Search className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No results found for "{query}"</p>
              <p className="text-sm text-gray-400 mt-1">Try different keywords</p>
            </div>
          )}

          {!searchData && (
            <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
              <Brain className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Search your meeting history with AI</p>
              <p className="text-sm text-gray-400 mt-1">Finds relevant meetings even when exact words don't match</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'topics' && (
        <div>
          {loadingTopics ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
            </div>
          ) : topics.length === 0 ? (
            <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
              <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No recurring topics yet</p>
              <p className="text-sm text-gray-400 mt-1">Topics appear after multiple meetings are analyzed</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {topics.map((t, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900 capitalize">{t.topic}</h3>
                    <span className="text-2xl font-bold text-indigo-600">{t.count}</span>
                  </div>
                  <p className="text-xs text-gray-500">meetings</p>
                  <div className="mt-3 w-full bg-gray-100 rounded-full h-1.5">
                    <div
                      className="bg-indigo-500 h-1.5 rounded-full"
                      style={{ width: `${Math.min(100, (t.count / Math.max(...topics.map(x => x.count))) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Knowledge
