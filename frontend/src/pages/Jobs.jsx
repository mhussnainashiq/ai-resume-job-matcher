import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Plus, Briefcase, Trash2 } from 'lucide-react'

export default function Jobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '', company: '', description: '',
    required_skills: '', preferred_skills: '',
    experience_required: '', education_required: '', location: ''
  })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    api.get('/api/jobs')
      .then(res => setJobs(res.data.jobs || []))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load jobs'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/api/jobs', {
        ...form,
        required_skills: form.required_skills.split(',').map(s => s.trim()).filter(Boolean),
        preferred_skills: form.preferred_skills.split(',').map(s => s.trim()).filter(Boolean),
      })
      setShowForm(false)
      setForm({ title: '', company: '', description: '', required_skills: '', preferred_skills: '', experience_required: '', education_required: '', location: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create job')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id, isSample) => {
    if (isSample) return
    if (!window.confirm('Delete this job?')) return
    try {
      await api.delete(`/api/jobs/${id}`)
      setJobs(j => j.filter(x => x.id !== id))
    } catch (err) {
      setError(err.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Job Descriptions</h1>
          <p>Sample jobs and your own listings for matching</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} style={{ verticalAlign: 'middle', marginRight: 4 }} /> Add Job
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>New Job Description</h3>
          <form onSubmit={handleCreate}>
            <div className="grid-2">
              <div className="form-group">
                <label>Title *</label>
                <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Company *</label>
                <input value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} required />
              </div>
            </div>
            <div className="form-group">
              <label>Description *</label>
              <textarea rows={5} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} required />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label>Required skills (comma-separated)</label>
                <input value={form.required_skills} onChange={e => setForm({ ...form, required_skills: e.target.value })} placeholder="python, fastapi, docker" />
              </div>
              <div className="form-group">
                <label>Preferred skills (comma-separated)</label>
                <input value={form.preferred_skills} onChange={e => setForm({ ...form, preferred_skills: e.target.value })} placeholder="aws, kubernetes" />
              </div>
            </div>
            <div className="grid-3">
              <div className="form-group">
                <label>Experience</label>
                <input value={form.experience_required} onChange={e => setForm({ ...form, experience_required: e.target.value })} placeholder="3+ years" />
              </div>
              <div className="form-group">
                <label>Education</label>
                <input value={form.education_required} onChange={e => setForm({ ...form, education_required: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save Job'}</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="loading"><div className="spinner" /> Loading...</div>
      ) : jobs.length === 0 ? (
        <div className="empty-state card">
          <Briefcase size={40} color="#94a3b8" style={{ marginBottom: '0.75rem' }} />
          <h3>No jobs</h3>
          <p>Add a job description or wait for samples to load.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {jobs.map(j => (
            <div key={j.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <Link to={`/jobs/${j.id}`} style={{ fontWeight: 600, fontSize: 15 }}>{j.title}</Link>
                <div style={{ fontSize: 13, color: 'var(--gray-500)', marginTop: 2 }}>
                  {j.company} {j.location && `· ${j.location}`}
                  {j.is_sample && <span className="badge badge-blue" style={{ marginLeft: 8 }}>Sample</span>}
                </div>
                <div style={{ marginTop: 6 }}>
                  {(j.required_skills || []).slice(0, 6).map(s => <span key={s} className="skill-tag">{s}</span>)}
                </div>
              </div>
              {!j.is_sample && (
                <button className="btn-secondary btn-sm" onClick={() => handleDelete(j.id, j.is_sample)}>
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
