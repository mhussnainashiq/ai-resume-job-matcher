import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

export default function Profile() {
  const { user, setUser } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [email, setEmail] = useState(user?.email || '')
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    setError('')
    try {
      const res = await api.put('/api/auth/me', { full_name: fullName, email })
      setUser(res.data)
      setMsg('Profile updated successfully')
    } catch (err) {
      setError(err.response?.data?.detail || 'Update failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Profile & Settings</h1>
        <p>Manage your account information</p>
      </div>

      {msg && <div className="alert alert-success">{msg}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ maxWidth: 480 }}>
        <form onSubmit={handleSave}>
          <div className="form-group">
            <label>Full name</label>
            <input value={fullName} onChange={e => setFullName(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Member since</label>
            <input value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'} disabled />
          </div>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save changes'}
          </button>
        </form>
      </div>

      <div className="card" style={{ maxWidth: 480, marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '0.5rem' }}>Data management</h3>
        <p style={{ fontSize: 14, color: 'var(--gray-600)', marginBottom: '0.75rem' }}>
          To delete a resume and its associated analyses, go to the Resumes page and use the delete button.
          Job applications and saved jobs can be managed from their respective pages.
        </p>
      </div>
    </div>
  )
}
