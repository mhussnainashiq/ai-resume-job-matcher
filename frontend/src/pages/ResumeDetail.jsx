import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft } from 'lucide-react'

export default function ResumeDetail() {
  const { id } = useParams()
  const [resume, setResume] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/api/resumes/${id}`)
      .then(res => setResume(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading"><div className="spinner" /> Loading...</div>
  if (error) return <div className="alert alert-error">{error}</div>
  if (!resume) return null

  const p = resume.profile || {}

  return (
    <div>
      <Link to="/resumes" style={{ display: 'inline-flex', alignItems: 'center', gap: 4, marginBottom: '1rem', fontSize: 14 }}>
        <ArrowLeft size={16} /> Back to resumes
      </Link>
      <div className="page-header">
        <h1>{resume.original_filename}</h1>
        <p>Parsed profile and analysis</p>
      </div>

      <div className="grid-2" style={{ marginBottom: '1.25rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem' }}>Contact & Summary</h3>
          <p><strong>Name:</strong> {p.name || '—'}</p>
          <p><strong>Email:</strong> {p.email || '—'}</p>
          <p><strong>Phone:</strong> {p.phone || '—'}</p>
          <p style={{ marginTop: '0.75rem' }}><strong>Summary:</strong></p>
          <p style={{ color: 'var(--gray-600)', fontSize: 14 }}>{p.summary || 'Not extracted'}</p>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem' }}>Completeness: {p.completeness_score?.toFixed(0) || 0}%</h3>
          <div style={{ background: 'var(--gray-100)', borderRadius: 6, height: 10, marginBottom: '1rem' }}>
            <div style={{ width: `${p.completeness_score || 0}%`, height: '100%', background: 'var(--blue)', borderRadius: 6 }} />
          </div>
          {p.strengths?.length > 0 && (
            <>
              <p style={{ fontWeight: 500, color: 'var(--success)', marginBottom: 4 }}>Strengths</p>
              <ul style={{ paddingLeft: '1.2rem', fontSize: 14, marginBottom: '0.75rem' }}>
                {p.strengths.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </>
          )}
          {p.weaknesses?.length > 0 && (
            <>
              <p style={{ fontWeight: 500, color: 'var(--warning)', marginBottom: 4 }}>Areas to improve</p>
              <ul style={{ paddingLeft: '1.2rem', fontSize: 14, marginBottom: '0.75rem' }}>
                {p.weaknesses.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </>
          )}
          {p.suggestions?.length > 0 && (
            <>
              <p style={{ fontWeight: 500, marginBottom: 4 }}>Suggestions</p>
              <ul style={{ paddingLeft: '1.2rem', fontSize: 14 }}>
                {p.suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </>
          )}
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Skills ({p.skills?.length || 0})</h3>
        <div>
          {(p.skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}
          {(!p.skills || p.skills.length === 0) && <p style={{ color: 'var(--gray-500)' }}>No skills extracted</p>}
        </div>
      </div>

      {p.experience?.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>Experience</h3>
          {p.experience.map((e, i) => (
            <div key={i} style={{ marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--gray-100)' }}>
              <div style={{ fontWeight: 500 }}>{e.title}</div>
              {e.duration && <div style={{ fontSize: 12, color: 'var(--gray-500)' }}>{e.duration}</div>}
              <p style={{ fontSize: 14, color: 'var(--gray-600)', marginTop: 4 }}>{e.description}</p>
            </div>
          ))}
        </div>
      )}

      {p.education?.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>Education</h3>
          {p.education.map((e, i) => (
            <div key={i} style={{ marginBottom: '0.5rem' }}>
              <div style={{ fontWeight: 500 }}>{e.degree}</div>
              <div style={{ fontSize: 13, color: 'var(--gray-500)' }}>{e.institution}</div>
            </div>
          ))}
        </div>
      )}

      {p.projects?.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem' }}>Projects</h3>
          {p.projects.map((pr, i) => (
            <div key={i} style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 500 }}>{pr.name}</div>
              <p style={{ fontSize: 14, color: 'var(--gray-600)' }}>{pr.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
