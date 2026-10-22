import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft, Bookmark } from 'lucide-react'

export default function JobDetail() {
  const { id } = useParams()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get(`/api/jobs/${id}`)
      .then(res => setJob(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [id])

  const handleSave = async () => {
    try {
      await api.post('/api/applications/saved', { job_id: parseInt(id) })
      setSaved(true)
    } catch (err) {
      if (err.response?.status === 400) setSaved(true)
      else setError(err.response?.data?.detail || 'Failed to save')
    }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading...</div>
  if (error) return <div className="alert alert-error">{error}</div>
  if (!job) return null

  return (
    <div>
      <Link to="/jobs" style={{ display: 'inline-flex', alignItems: 'center', gap: 4, marginBottom: '1rem', fontSize: 14 }}>
        <ArrowLeft size={16} /> Back to jobs
      </Link>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>
          <h1>{job.title}</h1>
          <p>{job.company} {job.location && `· ${job.location}`}
            {job.is_sample && <span className="badge badge-blue" style={{ marginLeft: 8 }}>Sample (not a real vacancy)</span>}
          </p>
        </div>
        <button className="btn-secondary" onClick={handleSave} disabled={saved}>
          <Bookmark size={16} style={{ verticalAlign: 'middle', marginRight: 4 }} />
          {saved ? 'Saved' : 'Save Job'}
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Description</h3>
        <p style={{ whiteSpace: 'pre-wrap', fontSize: 14, lineHeight: 1.6 }}>{job.description}</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '0.5rem' }}>Required Skills</h3>
          {(job.required_skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}
          {(!job.required_skills || !job.required_skills.length) && <p style={{ color: 'var(--gray-500)' }}>—</p>}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '0.5rem' }}>Preferred Skills</h3>
          {(job.preferred_skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}
          {(!job.preferred_skills || !job.preferred_skills.length) && <p style={{ color: 'var(--gray-500)' }}>—</p>}
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.25rem' }}>
        <p><strong>Experience:</strong> {job.experience_required || '—'}</p>
        <p><strong>Education:</strong> {job.education_required || '—'}</p>
      </div>
    </div>
  )
}
