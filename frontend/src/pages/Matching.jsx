import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Matching() {
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [resumeId, setResumeId] = useState('')
  const [jobId, setJobId] = useState('')
  const [method, setMethod] = useState('hybrid')
  const [result, setResult] = useState(null)
  const [gap, setGap] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])

  useEffect(() => {
    Promise.all([
      api.get('/api/resumes'),
      api.get('/api/jobs'),
      api.get('/api/matching/history'),
    ]).then(([r, j, h]) => {
      setResumes(r.data.resumes || [])
      setJobs(j.data.jobs || [])
      setHistory(h.data || [])
    }).catch(() => {})
  }, [])

  const runMatch = async () => {
    if (!resumeId || !jobId) {
      setError('Select both a resume and a job')
      return
    }
    setError('')
    setLoading(true)
    setResult(null)
    setGap(null)
    try {
      const [matchRes, gapRes] = await Promise.all([
        api.post('/api/matching/analyze', {
          resume_id: parseInt(resumeId),
          job_id: parseInt(jobId),
          method,
        }),
        api.get('/api/matching/skill-gap', {
          params: { resume_id: resumeId, job_id: jobId }
        }),
      ])
      setResult(matchRes.data)
      setGap(gapRes.data)
      // refresh history
      const h = await api.get('/api/matching/history')
      setHistory(h.data || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Match failed')
    } finally {
      setLoading(false)
    }
  }

  const scoreClass = (s) => s >= 70 ? 'score-high' : s >= 40 ? 'score-mid' : 'score-low'

  return (
    <div>
      <div className="page-header">
        <h1>Match Analysis</h1>
        <p>Compare a resume against a job description with explainable scores</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="grid-3">
          <div className="form-group">
            <label>Resume</label>
            <select value={resumeId} onChange={e => setResumeId(e.target.value)}>
              <option value="">Select resume...</option>
              {resumes.map(r => (
                <option key={r.id} value={r.id}>{r.original_filename}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Job</label>
            <select value={jobId} onChange={e => setJobId(e.target.value)}>
              <option value="">Select job...</option>
              {jobs.map(j => (
                <option key={j.id} value={j.id}>{j.title} — {j.company}{j.is_sample ? ' (Sample)' : ''}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Method</label>
            <select value={method} onChange={e => setMethod(e.target.value)}>
              <option value="hybrid">Hybrid (TF-IDF + Semantic)</option>
              <option value="tfidf">TF-IDF only</option>
              <option value="semantic">Semantic only</option>
            </select>
          </div>
        </div>
        <button className="btn-primary" onClick={runMatch} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Match Analysis'}
        </button>
        <p style={{ fontSize: 12, color: 'var(--gray-500)', marginTop: 8 }}>
          Scores are compatibility heuristics based on skill coverage and text similarity — not hiring probability.
        </p>
      </div>

      {result && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div className="card" style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginBottom: '1rem' }}>
            <div className={`score-circle ${scoreClass(result.overall_score)}`}>
              {result.overall_score}%
            </div>
            <div>
              <h3 style={{ marginBottom: 4 }}>{result.job_title || 'Match Result'}</h3>
              <p style={{ color: 'var(--gray-500)', fontSize: 14 }}>{result.job_company} · Method: {result.matching_method}</p>
            </div>
          </div>

          <div className="grid-2" style={{ marginBottom: '1rem' }}>
            <div className="card">
              <h3 style={{ marginBottom: '0.75rem', fontSize: '0.95rem' }}>Component Scores</h3>
              {Object.entries(result.component_scores || {}).map(([k, v]) => (
                <div key={k} style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                    <span>{k.replace(/_/g, ' ')}</span>
                    <span style={{ fontWeight: 600 }}>{v}%</span>
                  </div>
                  <div style={{ background: 'var(--gray-100)', borderRadius: 4, height: 6, marginTop: 2 }}>
                    <div style={{ width: `${v}%`, height: '100%', background: 'var(--blue)', borderRadius: 4 }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="card">
              <h3 style={{ marginBottom: '0.5rem', fontSize: '0.95rem' }}>Matched Required</h3>
              <div style={{ marginBottom: '0.75rem' }}>
                {(result.matched_required_skills || []).map(s => <span key={s} className="skill-tag matched">{s}</span>)}
                {!(result.matched_required_skills || []).length && <span style={{ color: 'var(--gray-500)', fontSize: 13 }}>None</span>}
              </div>
              <h3 style={{ marginBottom: '0.5rem', fontSize: '0.95rem' }}>Missing Required</h3>
              <div>
                {(result.missing_required_skills || []).map(s => <span key={s} className="skill-tag missing">{s}</span>)}
                {!(result.missing_required_skills || []).length && <span style={{ color: 'var(--gray-500)', fontSize: 13 }}>None</span>}
              </div>
            </div>
          </div>

          {result.strengths?.length > 0 && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h3 style={{ marginBottom: 6, color: 'var(--success)' }}>Strengths</h3>
              <ul style={{ paddingLeft: '1.2rem', fontSize: 14 }}>
                {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          {result.suggestions?.length > 0 && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h3 style={{ marginBottom: 6 }}>Suggestions</h3>
              <ul style={{ paddingLeft: '1.2rem', fontSize: 14 }}>
                {result.suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {gap && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>Skill Gap Analysis</h3>
          <div className="grid-2">
            <div>
              <p style={{ fontWeight: 500, marginBottom: 4 }}>Demonstrated</p>
              {(gap.demonstrated_skills || []).map(s => <span key={s} className="skill-tag matched">{s}</span>)}
            </div>
            <div>
              <p style={{ fontWeight: 500, marginBottom: 4 }}>Learning Priorities</p>
              {(gap.learning_priorities || []).map(s => <span key={s} className="skill-tag missing">{s}</span>)}
            </div>
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--gray-200)', fontWeight: 600 }}>
            Recent Match History
          </div>
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Score</th>
                <th>Method</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(0, 10).map(h => (
                <tr key={h.id}>
                  <td>{h.job_title || `Job #${h.job_id}`}</td>
                  <td><span className={`badge ${h.overall_score >= 70 ? 'badge-green' : h.overall_score >= 40 ? 'badge-yellow' : 'badge-red'}`}>{h.overall_score}%</span></td>
                  <td>{h.matching_method}</td>
                  <td>{new Date(h.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
