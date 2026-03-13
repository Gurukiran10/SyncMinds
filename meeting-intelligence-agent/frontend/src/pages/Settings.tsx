import React from 'react'
import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '../lib/api'

const Settings: React.FC = () => {
  const { data: profile, refetch } = useQuery('settings-profile', async () => {
    const response = await api.get('/api/v1/users/me')
    return response.data
  })

  const [saving, setSaving] = useState(false)

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
    setSaving(false)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage profile and notification preferences.</p>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4 max-w-2xl">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
          <input value={timezone} onChange={(e) => setTimezone(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
          <input value={department} onChange={(e) => setDepartment(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
          <input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>

        <div className="pt-2 border-t border-gray-200 space-y-2">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={emailEnabled} onChange={(e) => setEmailEnabled(e.target.checked)} />
            Email notifications
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={slackEnabled} onChange={(e) => setSlackEnabled(e.target.checked)} />
            Slack notifications
          </label>
        </div>

        <button type="submit" disabled={saving} className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-60">
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}

export default Settings
