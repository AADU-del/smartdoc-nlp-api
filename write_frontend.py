import os

files = {
"frontend/src/pages/Login.jsx": '''import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const response = await axios.post("http://localhost:8000/api/v1/auth/login", { email, password })
      login(response.data.access_token)
      navigate("/dashboard")
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Welcome back</h1>
        <p>Sign in to your SmartDoc account</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn" type="submit" disabled={loading}>{loading ? "Signing in..." : "Sign in"}</button>
        </form>
        <div className="link-text">Don\'t have an account? <Link to="/register">Register</Link></div>
      </div>
    </div>
  )
}''',

"frontend/src/pages/Register.jsx": '''import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"

export default function Register() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const response = await axios.post("http://localhost:8000/api/v1/auth/register", { email, password })
      login(response.data.access_token)
      navigate("/dashboard")
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create account</h1>
        <p>Start analyzing documents with AI</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" placeholder="Min 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn" type="submit" disabled={loading}>{loading ? "Creating account..." : "Create account"}</button>
        </form>
        <div className="link-text">Already have an account? <Link to="/login">Sign in</Link></div>
      </div>
    </div>
  )
}''',

"frontend/src/pages/Dashboard.jsx": '''import { useState, useEffect } from "react"
import { useNavigate, Link } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"

export default function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const { token } = useAuth()
  const navigate = useNavigate()

  useEffect(() => { fetchDocuments() }, [])

  const fetchDocuments = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/v1/documents/", { headers: { Authorization: `Bearer ${token}` } })
      setDocuments(response.data)
    } catch (err) {
      console.error("Failed to fetch documents", err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })

  return (
    <>
      <Navbar />
      <div className="container page">
        <div className="page-header">
          <h1>My Documents</h1>
          <Link to="/upload"><button className="btn btn-small">+ Upload New</button></Link>
        </div>
        {loading ? <div className="loading">Loading documents...</div> : documents.length === 0 ? (
          <div className="empty-state">
            <h2>No documents yet</h2>
            <p>Upload your first document to get NLP analysis</p>
            <br />
            <Link to="/upload"><button className="btn btn-small">Upload Document</button></Link>
          </div>
        ) : (
          <div className="doc-grid">
            {documents.map((doc) => (
              <div key={doc.id} className="doc-card" onClick={() => navigate(`/results/${doc.id}`)}>
                <h3>{doc.filename}</h3>
                <span className={`status-badge status-${doc.status}`}>{doc.status}</span>
                <div className="doc-date">{formatDate(doc.created_at)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}''',

"frontend/src/pages/Upload.jsx": '''import { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"

export default function Upload() {
  const [filename, setFilename] = useState("")
  const [content, setContent] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const { token } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const response = await axios.post("http://localhost:8000/api/v1/documents/", { filename, content }, { headers: { Authorization: `Bearer ${token}` } })
      navigate(`/results/${response.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="container page">
        <div className="page-header"><h1>Upload Document</h1></div>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit} style={{ maxWidth: "700px" }}>
          <div className="form-group">
            <label>Document Name</label>
            <input type="text" placeholder="e.g. report.txt" value={filename} onChange={(e) => setFilename(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Document Content</label>
            <textarea placeholder="Paste your document text here..." value={content} onChange={(e) => setContent(e.target.value)} required style={{ minHeight: "200px" }} />
          </div>
          <button className="btn" type="submit" disabled={loading}>{loading ? "Uploading & Analysing..." : "Upload & Analyse"}</button>
        </form>
      </div>
    </>
  )
}''',

"frontend/src/pages/Results.jsx": '''import { useState, useEffect } from "react"
import { useParams, Link } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"

export default function Results() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  const { token } = useAuth()

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const statusRes = await axios.get(`http://localhost:8000/api/v1/documents/${id}/status`, { headers: { Authorization: `Bearer ${token}` } })
        if (statusRes.data.status === "done" || statusRes.data.status === "failed") {
          clearInterval(interval)
          const fullRes = await axios.get(`http://localhost:8000/api/v1/documents/${id}`, { headers: { Authorization: `Bearer ${token}` } })
          setDocument(fullRes.data)
          setLoading(false)
        }
      } catch (err) {
        clearInterval(interval)
        setLoading(false)
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [id])

  const getSentimentClass = (s) => s ? `sentiment-${s.toLowerCase()}` : ""

  if (loading) return (
    <>
      <Navbar />
      <div className="container page">
        <div className="loading"><h2>Analysing document...</h2><p style={{ marginTop: "12px", color: "#64748b" }}>Running NLP pipeline...</p></div>
      </div>
    </>
  )

  const analysis = document?.analysis_result

  return (
    <>
      <Navbar />
      <div className="container page">
        <Link to="/dashboard" className="back-btn">← Back to Dashboard</Link>
        <div className="page-header">
          <h1>{document?.filename}</h1>
          <span className={`status-badge status-${document?.status}`}>{document?.status}</span>
        </div>
        {!analysis ? <div className="empty-state"><h2>Analysis failed</h2></div> : (
          <div className="results-grid">
            <div className="result-card full-width"><h3>Summary</h3><p>{analysis.summary}</p></div>
            <div className="result-card"><h3>Keywords</h3><div className="keywords-list">{analysis.keywords?.map((kw, i) => <span key={i} className="keyword-tag">{kw}</span>)}</div></div>
            <div className="result-card"><h3>Sentiment</h3>
              <div className="sentiment-display">
                <div className={`sentiment-value ${getSentimentClass(analysis.sentiment)}`}>{analysis.sentiment === "POSITIVE" ? "Positive" : analysis.sentiment === "NEGATIVE" ? "Negative" : "Neutral"}</div>
                <div style={{ color: "#94a3b8", fontSize: "0.9rem" }}>Confidence: {((analysis.sentiment_score || 0) * 100).toFixed(1)}%</div>
                <div className="score-bar"><div className="score-fill" style={{ width: `${(analysis.sentiment_score || 0) * 100}%` }} /></div>
              </div>
            </div>
            <div className="result-card full-width"><h3>Named Entities</h3>
              <div className="entities-list">
                {analysis.entities?.length > 0 ? analysis.entities.map((e, i) => (
                  <div key={i} className="entity-item"><span>{e.text}</span><span className="entity-label">{e.label}</span></div>
                )) : <p style={{ color: "#64748b" }}>No entities found</p>}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}''',

"frontend/src/components/Navbar.jsx": '''import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate("/login") }

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/dashboard" className="navbar-brand">SmartDoc</Link>
        <div className="navbar-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/upload">Upload</Link>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </nav>
  )
}''',

"frontend/src/components/PrivateRoute.jsx": '''import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}''',
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Written: {path}")

print("\nAll files written successfully!")