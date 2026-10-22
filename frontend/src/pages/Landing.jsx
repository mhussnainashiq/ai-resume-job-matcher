import React from 'react'
import { Link } from 'react-router-dom'
import { FileText, GitCompare, Sparkles, BarChart3, Shield, Zap } from 'lucide-react'
import '../styles/landing.css'

export default function Landing() {
  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="landing-logo">Resume<span>Match</span></div>
        <div className="landing-nav-actions">
          <Link to="/login" className="btn-secondary">Log in</Link>
          <Link to="/register" className="btn-primary" style={{ textDecoration: 'none' }}>Get Started</Link>
        </div>
      </nav>
      <section className="hero">
        <h1>AI-Powered Resume & Job Matching</h1>
        <p className="hero-sub">
          Upload your resume, analyze skills, match against job descriptions with explainable scores,
          identify skill gaps, and track applications — all powered by genuine NLP and ML.
        </p>
        <div className="hero-actions">
          <Link to="/register" className="btn-primary btn-lg">Start Free</Link>
          <Link to="/login" className="btn-secondary btn-lg">Sign In</Link>
        </div>
      </section>
      <section className="features">
        <div className="feature-card">
          <FileText size={28} color="#2563eb" />
          <h3>Resume Parsing</h3>
          <p>Extract skills, experience, education and more from PDF or DOCX with rule-based NLP.</p>
        </div>
        <div className="feature-card">
          <GitCompare size={28} color="#2563eb" />
          <h3>Explainable Matching</h3>
          <p>TF-IDF + semantic similarity with transparent component scores — not black-box magic.</p>
        </div>
        <div className="feature-card">
          <Sparkles size={28} color="#2563eb" />
          <h3>Skill Gap Analysis</h3>
          <p>See matched and missing skills with learning priorities based on job requirements.</p>
        </div>
        <div className="feature-card">
          <BarChart3 size={28} color="#2563eb" />
          <h3>Dashboard & Tracking</h3>
          <p>Track applications, view analytics, and manage your job search in one place.</p>
        </div>
        <div className="feature-card">
          <Shield size={28} color="#2563eb" />
          <h3>Secure & Private</h3>
          <p>JWT auth, password hashing, ownership checks. Your data stays local with SQLite.</p>
        </div>
        <div className="feature-card">
          <Zap size={28} color="#2563eb" />
          <h3>No Paid API Required</h3>
          <p>Works offline with TF-IDF baseline. Optional Sentence Transformers for semantic match.</p>
        </div>
      </section>
      <footer className="landing-footer">
        <p>AI Resume Job Matcher — Portfolio project demonstrating full-stack AI/ML engineering.</p>
      </footer>
    </div>
  )
}
