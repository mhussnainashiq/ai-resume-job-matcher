import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { ClipboardList } from 'lucide-react'

const STATUSES = ['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn']

export default function Applications() {
  const [apps, setApps] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ job_id: '', status: 'Applied', notes: '', applied_date: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([
      api.get('/api/applications/track', { params: filter ? { status: filter } : {} }),
      api.get('/api/jobs'),
    ]).then(([a, j]) => {
      setApps(a.data || [])
      setJobs(j.data.jobs || [])
    }).catch(err => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [filter])

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/applications/track', {
        job_id: parseInt(form.job_id),
        status: form.status,
        notes: form.notes || null,
        applied_date: form.applied_date || null,
      })
      setShowForm(false)
      setForm({ job_id: '', status: 'Applied', notes: '', applied_date: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create')
    } finally {
      setSaving(false)
    }
  }

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/api/applications/track/${id}`, { status })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Update failed')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this application?')) return
    try {
      await api.delete(`/api/applications/track/${id}`)
      setApps(a => a.filter(x => x.id !== id))
    } catch (err) {
      setError(err.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Application Tracker</h1>
          <p>Track status of your job applications</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>Add Application</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <form onSubmit={handleCreate}>
            <div className="grid-2">
              <div className="form-group">
                <label>Job</label>
                <select value={form.job_id} onChange={e => setForm({ ...form, job_id: e.target.value })} required>
                  <option value="">Select job...</option>
                  {jobs.map(j => <option key={j.id} value={j.id}>{j.title} — {j.company}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Status</label>
                <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label>Applied date</label>
                <input type="date" value={form.applied_date} onChange={e => setForm({ ...form, applied_date: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Notes</label>
                <input value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
              </div>
            </div>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
          </form>
        </div>
      )}

      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button className={`btn-sm ${!filter ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setFilter('')}>All</button>
        {STATUSES.map(s => (
          <button key={s} className={`btn-sm ${filter === s ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setFilter(s)}>{s}</button>
        ))}
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /> Loading...</div>
      ) : apps.length === 0 ? (
        <div className="empty-state card">
          <ClipboardList size={40} color="#94a3b8" style={{ marginBottom: '0.75rem' }} />
          <h3>No applications</h3>
          <p>Start tracking applications to monitor your job search progress.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Company</th>
                <th>Status</th>
                <th>Applied</th>
                <th>Notes</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {apps.map(a => (
                <tr key={a.id}>
                  <td style={{ fontWeight: 500 }}>{a.job_title}</td>
                  <td>{a.job_company}</td>
                  <td>
                    <select
                      value={a.status}
                      onChange={e => updateStatus(a.id, e.target.value)}
                      style={{ width: 'auto', padding: '0.3rem 0.5rem', fontSize: 13 }}
                    >
                      {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td>{a.applied_date || '—'}</td>
                  <td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.notes || '—'}</td>
                  <td>
                    <button className="btn-secondary btn-sm" onClick={() => handleDelete(a.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
