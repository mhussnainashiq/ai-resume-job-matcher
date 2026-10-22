import React, { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Upload, FileText, Trash2 } from 'lucide-react'

export default function Resumes() {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()

  const load = () => {
    setLoading(true)
    api.get('/api/resumes')
      .then(res => setResumes(res.data.resumes || []))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load resumes'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleUpload = async (file) => {
    if (!file) return
    setError('')
    setSuccess('')
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/api/resumes/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess(`Uploaded: ${res.data.original_filename}`)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this resume and all related analyses?')) return
    try {
      await api.delete(`/api/resumes/${id}`)
      setResumes(r => r.filter(x => x.id !== id))
    } catch (err) {
      setError(err.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Resumes</h1>
        <p>Upload PDF or DOCX resumes for AI analysis</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div
        className={`card upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        style={{ textAlign: 'center', padding: '2.5rem', cursor: 'pointer', marginBottom: '1.5rem', borderStyle: 'dashed', borderWidth: 2 }}
      >
        <Upload size={32} color="#2563eb" style={{ marginBottom: '0.75rem' }} />
        <p style={{ fontWeight: 500, marginBottom: '0.25rem' }}>
          {uploading ? 'Uploading & parsing...' : 'Drag & drop a resume, or click to browse'}
        </p>
        <p style={{ fontSize: 13, color: 'var(--gray-500)' }}>PDF or DOCX, max 5 MB</p>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          onChange={e => handleUpload(e.target.files[0])}
        />
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /> Loading...</div>
      ) : resumes.length === 0 ? (
        <div className="empty-state card">
          <FileText size={40} color="#94a3b8" style={{ marginBottom: '0.75rem' }} />
          <h3>No resumes yet</h3>
          <p>Upload your first resume to get started with analysis and matching.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Type</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th>Skills</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {resumes.map(r => (
                <tr key={r.id}>
                  <td>
                    <Link to={`/resumes/${r.id}`} style={{ fontWeight: 500 }}>
                      {r.original_filename}
                    </Link>
                  </td>
                  <td><span className="badge badge-gray">{r.file_type}</span></td>
                  <td>{(r.file_size / 1024).toFixed(1)} KB</td>
                  <td>{new Date(r.created_at).toLocaleDateString()}</td>
                  <td>{r.profile?.skills?.length || 0}</td>
                  <td>
                    <button className="btn-secondary btn-sm" onClick={() => handleDelete(r.id)} title="Delete">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <style>{`.upload-zone.drag-over { border-color: var(--blue); background: var(--blue-bg); }`}</style>
    </div>
  )
}
