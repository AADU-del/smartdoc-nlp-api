import { useState, useEffect } from "react"
import { useParams, Link, useNavigate } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"
import { API_BASE_URL } from "../api/config"

export default function Results() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const { token } = useAuth()

  useEffect(() => {
    let isMounted = true

    const fetchDocumentData = async () => {
      try {
        const statusRes = await axios.get(`${API_BASE_URL}/documents/${id}/status`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        const currentStatus = statusRes.data.status

        if (currentStatus === "done" || currentStatus === "failed") {
          const fullRes = await axios.get(`${API_BASE_URL}/documents/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          if (isMounted) {
            setDocument(fullRes.data)
            setLoading(false)
          }
          return true // Done processing
        }
      } catch (err) {
        if (isMounted) {
          setError(err.response?.data?.detail || "Failed to load document")
          setLoading(false)
        }
        return true
      }
      return false
    }

    // Instant check on mount
    fetchDocumentData().then((isDone) => {
      if (isDone || !isMounted) return
      // Poll every 2s if still pending/processing
      const interval = setInterval(async () => {
        const done = await fetchDocumentData()
        if (done) clearInterval(interval)
      }, 2000)

      return () => clearInterval(interval)
    })

    return () => {
      isMounted = false
    }
  }, [id, token])

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this document?")) return
    try {
      await axios.delete(`${API_BASE_URL}/documents/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      navigate("/dashboard")
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete document")
    }
  }

  const handleExportJSON = () => {
    if (!document) return
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(document, null, 2))
    const downloadAnchor = window.document.createElement("a")
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `${document.filename}_analysis.json`)
    window.document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  const getSentimentClass = (s) => (s ? `sentiment-${s.toLowerCase()}` : "")

  if (loading)
    return (
      <>
        <Navbar />
        <div className="container page">
          <div className="loading">
            <h2>Analysing document...</h2>
            <p style={{ marginTop: "12px", color: "#64748b" }}>Running spaCy NLP pipeline...</p>
          </div>
        </div>
      </>
    )

  if (error)
    return (
      <>
        <Navbar />
        <div className="container page">
          <Link to="/dashboard" className="back-btn">← Back to Dashboard</Link>
          <div className="empty-state">
            <h2>Error Loading Document</h2>
            <p style={{ color: "#ef4444", marginTop: "8px" }}>{error}</p>
          </div>
        </div>
      </>
    )

  const analysis = document?.analysis_result

  return (
    <>
      <Navbar />
      <div className="container page">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Link to="/dashboard" className="back-btn">← Back to Dashboard</Link>
          <div style={{ display: "flex", gap: "10px" }}>
            {analysis && (
              <button className="btn btn-small" onClick={handleExportJSON}>
                📥 Export JSON
              </button>
            )}
            <button className="btn btn-small" style={{ background: "#ef4444" }} onClick={handleDelete}>
              🗑️ Delete
            </button>
          </div>
        </div>

        <div className="page-header" style={{ marginTop: "16px" }}>
          <h1>{document?.filename}</h1>
          <span className={`status-badge status-${document?.status}`}>{document?.status}</span>
        </div>

        {!analysis ? (
          <div className="empty-state">
            <h2>Analysis Failed or Pending</h2>
            <p style={{ color: "#64748b" }}>NLP processing was unable to complete for this document.</p>
          </div>
        ) : (
          <div className="results-grid">
            <div className="result-card full-width">
              <h3>Summary</h3>
              <p>{analysis.summary || "No summary available."}</p>
            </div>

            <div className="result-card">
              <h3>Keywords</h3>
              <div className="keywords-list">
                {analysis.keywords?.length > 0 ? (
                  analysis.keywords.map((kw, i) => (
                    <span key={i} className="keyword-tag">
                      {kw}
                    </span>
                  ))
                ) : (
                  <p style={{ color: "#64748b" }}>No keywords extracted.</p>
                )}
              </div>
            </div>

            <div className="result-card">
              <h3>Sentiment Analysis</h3>
              <div className="sentiment-display">
                <div className={`sentiment-value ${getSentimentClass(analysis.sentiment)}`}>
                  {analysis.sentiment === "POSITIVE"
                    ? "Positive"
                    : analysis.sentiment === "NEGATIVE"
                    ? "Negative"
                    : "Neutral"}
                </div>
                <div style={{ color: "#94a3b8", fontSize: "0.9rem", marginTop: "6px" }}>
                  Confidence Score: {((analysis.sentiment_score || 0) * 100).toFixed(1)}%
                </div>
                <div className="score-bar">
                  <div
                    className="score-fill"
                    style={{ width: `${(analysis.sentiment_score || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="result-card full-width">
              <h3>Named Entities (NER)</h3>
              <div className="entities-list">
                {analysis.entities?.length > 0 ? (
                  analysis.entities.map((e, i) => (
                    <div key={i} className="entity-item">
                      <span>{e.text}</span>
                      <span className="entity-label">{e.label}</span>
                    </div>
                  ))
                ) : (
                  <p style={{ color: "#64748b" }}>No entities found in text.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}