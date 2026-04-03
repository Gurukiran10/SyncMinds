import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { User, Bell, Check } from 'lucide-react'
import { api } from '../lib/api'
import { Skeleton } from '../components/ui/Skeleton'

const Toggle: React.FC<{ checked: boolean; onChange: (v: boolean) => void; label: string; description?: string }> = ({
  checked, onChange, label, description,
}) => (
  <div className="flex items-center justify-between gap-4 py-3.5">
    <div>
      <p className="text-sm font-medium text-gray-900">{label}</p>
      {description && <p className="text-xs text-gray-400 mt-0.5">{description}</p>}
    </div>
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 flex-shrink-0 ${
        checked ? 'bg-primary-600' : 'bg-gray-200'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  </div>
)

const TIMEZONES = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
  'America/Toronto', 'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Istanbul',
  'Asia/Dubai', 'Asia/Kolkata', 'Asia/Singapore', 'Asia/Tokyo', 'Australia/Sydney',
]

const Settings: React.FC = () => {
  const { data: profile, isLoading, refetch } = useQuery('settings-profile', async () => {
    const response = await api.get('/api/v1/users/me')
    return response.data
  })

  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [fullName, setFullName] = useState('')
  const [timezone, setTimezone] = useState('UTC')
  const [department, setDepartment] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [emailEnabled, setEmailEnabled] = useState(true)
  const [slackEnabled, setSlackEnabled] = useState(true)

  React.useEffect(() => {
    if (!profile) return
    setFullName(profile.full_name || '')
    setTimezone(profile.timezone || 'UTC')
    setDepartment(profile.department || '')
    setJobTitle(profile.job_title || '')
    setEmailEnabled(profile.notification_settings?.email_enabled ?? true)
    setSlackEnabled(profile.notification_settings?.slack_enabled ?? true)
  }, [profile])

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setSaved(false)
    try {
      await api.patch('/api/v1/users/me', {
        full_name: fullName,
        timezone,
        department,
        job_title: jobTitle,
        notification_settings: {
          ...(profile?.notification_settings || {}),
          email_enabled: emailEnabled,
          slack_enabled: slackEnabled,
        },
      })
      await refetch()
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  const inputClass = 'w-full px-3.5 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none transition-colors'

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-2xl">
        <div>
          <Skeleton className="h-8 w-32 mb-1" />
          <Skeleton className="h-4 w-56 mt-2" />
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i}>
              <Skeleton className="h-3 w-24 mb-2" />
              <Skeleton className="h-10 w-full rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">Manage your profile and preferences.</p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-100">
            <User className="w-4 h-4 text-gray-400" />
            <h2 className="text-sm font-semibold text-gray-900">Profile</h2>
          </div>
          <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Full Name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputClass} placeholder="Your full name" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Department</label>
              <input value={department} onChange={(e) => setDepartment(e.target.value)} className={inputClass} placeholder="e.g. Engineering" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Job Title</label>
              <input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} className={inputClass} placeholder="e.g. Product Manager" />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Timezone</label>
              <select value={timezone} onChange={(e) => setTimezone(e.target.value)} className={inputClass}>
                {TIMEZONES.map(tz => <option key={tz} value={tz}>{tz}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-100">
            <Bell className="w-4 h-4 text-gray-400" />
            <h2 className="text-sm font-semibold text-gray-900">Notifications</h2>
          </div>
          <div className="px-6 divide-y divide-gray-50">
            <Toggle
              checked={emailEnabled}
              onChange={setEmailEnabled}
              label="Email notifications"
              description="Receive action item digests and meeting summaries by email"
            />
            <Toggle
              checked={slackEnabled}
              onChange={setSlackEnabled}
              label="Slack notifications"
              description="Get real-time alerts in Slack when you're mentioned or assigned"
            />
          </div>
        </div>

        {/* Save */}
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </>
            ) : 'Save Changes'}
          </button>
          {saved && (
            <span className="flex items-center gap-1.5 text-sm text-green-600 font-medium animate-pulse">
              <Check className="w-4 h-4" /> Saved
            </span>
          )}
        </div>
      </form>
    </div>
  )
}

export default Settings
