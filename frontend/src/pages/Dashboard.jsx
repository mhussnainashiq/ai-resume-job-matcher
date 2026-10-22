import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { FileText, Briefcase, GitCompare, Bookmark, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed']

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/api/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load stats'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /> Loading dashboard...</div>
  if (error) return <div className="alert alert-error">{error}</div>

  const appData = Object.entries(stats.application_stats || {}).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your resume analyses and job search activity</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        <div className="card stat-card">
          <div className="stat-icon"><FileText size={20} /></div>
          <div className="stat-value">{stats.total_resumes}</div>
          <div className="stat-label">Resumes</div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon"><Briefcase size={20} /></div>
          <div className="stat-value">{stats.total_jobs}</div>
          <div className="stat-label">Jobs Available</div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon"><GitCompare size={20} /></div>
          <div className="stat-value">{stats.total_analyses}</div>
          <div className="stat-label">Analyses</div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon"><TrendingUp size={20} /></div>
          <div className="stat-value">{stats.average_compatibility}%</div>
          <div className="stat-label">Avg Compatibility</div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Top Matched Skills</h3>
          {stats.top_matched_skills?.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats.top_matched_skills}>
                <XAxis dataKey="skill" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '2rem' }}>
              <p>No match data yet. Analyze a resume against a job to see skills.</p>
            </div>
          )}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Common Skill Gaps</h3>
          {stats.common_skill_gaps?.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats.common_skill_gaps}>
                <XAxis dataKey="skill" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '2rem' }}>
              <p>No skill gap data yet.</p>
            </div>
          )}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Recent Analyses</h3>
          {stats.recent_analyses?.length > 0 ? (
            <div>
              {stats.recent_analyses.map(a => (
                <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0', borderBottom: '1px solid var(--gray-100)' }}>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: 14 }}>{a.job_title}</div>
                    <div style={{ fontSize: 12, color: 'var(--gray-500)' }}>{a.company} · {a.method}</div>
                  </div>
                  <span className={`badge ${a.score >= 70 ? 'badge-green' : a.score >= 40 ? 'badge-yellow' : 'badge-red'}`}>
                    {a.score}%
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '1.5rem' }}>
              <p>No analyses yet. <Link to="/matching">Run a match</Link></p>
            </div>
          )}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Application Status</h3>
          {appData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={appData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                  {appData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '1.5rem' }}>
              <p>No applications tracked. <Link to="/applications">Start tracking</Link></p>
            </div>
          )}
          <div style={{ marginTop: '0.75rem', fontSize: 13, color: 'var(--gray-500)' }}>
            <Bookmark size={14} style={{ verticalAlign: 'middle' }} /> {stats.saved_jobs_count} saved jobs
          </div>
        </div>
      </div>

      <style>{`
        .stat-card { text-align: center; padding: 1.25rem 1rem; }
        .stat-icon { color: var(--blue); margin-bottom: 0.35rem; }
        .stat-value { font-size: 1.75rem; font-weight: 700; color: var(--navy); }
        .stat-label { font-size: 13px; color: var(--gray-500); margin-top: 0.15rem; }
      `}</style>
    </div>
  )
}
