import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import Dashboard from './pages/Dashboard'
import Meetings from './pages/Meetings'
import MeetingDetail from './pages/MeetingDetail'
import ActionItems from './pages/ActionItems'
import Mentions from './pages/Mentions'
import Analytics from './pages/Analytics'
import Integrations from './pages/Integrations'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Layout from './components/Layout'
import './index.css'
import { isAuthenticated } from './lib/auth'

const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return children
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={(
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            )}
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="meetings" element={<Meetings />} />
            <Route path="meetings/:id" element={<MeetingDetail />} />
            <Route path="action-items" element={<ActionItems />} />
            <Route path="mentions" element={<Mentions />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
