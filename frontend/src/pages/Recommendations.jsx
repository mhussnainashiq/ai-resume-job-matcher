import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Sparkles } from 'lucide-react'

export default function Recommendations() {
  const [resumes, setResumes] = useState([])
  const [resumeId, setResumeId] = useState('')
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/api/resumes').then(res => {
      const list = res.data.resumes || []
      setResumes(list)
      if (list.length) setResumeId(String(list[0].id))
    }).catch(() => {})
  }, [])

  const loadRecs = async () => {
    if (!resumeId) return
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/api/matching/recommendations', {
        params: { resume_id: resumeId, limit: 15 }
      })
      setRecs(res.data.recommendations || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (resumeId) loadRecs()
  }, [resumeId])

  return (
    <div>
      <div className="page-header">
        <h1>Job Recommendations</h1>
        <p>Jobs ranked by compatibility with your selected resume</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="form-group" style={{ maxWidth: 400 }}>
          <label>Select Resume</label>
          <select value={resumeId} onChange={e => setResumeId(e.target.value)}>
            <option value="">Select...</option>
            {resumes.map(r => (
              <option key={r.id} value={r.id}>{r.original_filename}</option>
            ))}
          </select>
        </div>
        {!resumes.length && (
          <p style={{ color: 'var(--gray-500)', fontSize: 14 }}>
            <Link to="/resumes">Upload a resume</Link> first to get recommendations.
          </p>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading"><div className="spinner" /> Computing recommendations...</div>
      ) : recs.length === 0 && resumeId ? (
        <div className="empty-state card">
          <Sparkles size={40} color="#94a3b8" style={{ marginBottom: '0.75rem' }} />
          <h3>No recommendations</h3>
          <p>Add more job descriptions or check that the resume has extracted skills.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {recs.map(r => (
            <div key={r.job_id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <Link to={`/jobs/${r.job_id}`} style={{ fontWeight: 600, fontSize: 15 }}>{r.title}</Link>
                  <div style={{ fontSize: 13, color: 'var(--gray-500)' }}>
                    {r.company}
                    {r.is_sample && <span className="badge badge-blue" style={{ marginLeft: 8 }}>Sample</span>}
                  </div>
                  <p style={{ fontSize: 13, marginTop: 6, color: 'var(--gray-600)' }}>{r.explanation}</p>
                  <div style={{ marginTop: 6 }}>
                    {(r.matched_skills || []).slice(0, 6).map(s => <span key={s} className="skill-tag matched">{s}</span>)}
                    {(r.missing_skills || []).slice(0, 4).map(s => <span key={s} className="skill-tag missing">{s}</span>)}
                  </div>
                </div>
                <span className={`badge ${r.overall_score >= 70 ? 'badge-green' : r.overall_score >= 40 ? 'badge-yellow' : 'badge-red'}`} style={{ fontSize: 14, padding: '0.35rem 0.7rem' }}>
                  {r.overall_score}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
