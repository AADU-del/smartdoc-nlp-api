import { useState, useEffect } from "react"
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
}