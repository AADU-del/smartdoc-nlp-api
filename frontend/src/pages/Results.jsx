import { useState, useEffect } from "react"
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
}