import { useState, useEffect } from "react"
import { useNavigate, Link } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"
import { API_BASE_URL } from "../api/config"

export default function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const { token } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDocuments(response.data)
    } catch (err) {
      console.error("Failed to fetch documents", err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (e, docId) => {
    e.stopPropagation() // Prevent card click navigation
    if (!window.confirm("Are you sure you want to delete this document?")) return

    try {
      await axios.delete(`${API_BASE_URL}/documents/${docId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDocuments(documents.filter((doc) => doc.id !== docId))
    } catch (err) {
      alert("Failed to delete document")
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ""
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric"
    })
  }

  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <>
      <Navbar />
      <div className="container page">
        <div className="page-header">
          <h1>My Documents</h1>
          <Link to="/upload">
            <button className="btn btn-small">+ Upload New</button>
          </Link>
        </div>

        {documents.length > 0 && (
          <div style={{ marginBottom: "20px" }}>
            <input
              type="text"
              placeholder="🔍 Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: "100%",
                maxWidth: "400px",
                padding: "10px 14px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "0.95rem"
              }}
            />
          </div>
        )}

        {loading ? (
          <div className="loading">Loading documents...</div>
        ) : filteredDocuments.length === 0 ? (
          <div className="empty-state">
            <h2>{searchTerm ? "No matching documents" : "No documents yet"}</h2>
            <p>{searchTerm ? "Try searching for a different term." : "Upload your first document to get NLP analysis"}</p>
            <br />
            <Link to="/upload">
              <button className="btn btn-small">Upload Document</button>
            </Link>
          </div>
        ) : (
          <div className="doc-grid">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="doc-card"
                onClick={() => navigate(`/results/${doc.id}`)}
                style={{ position: "relative" }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <h3 style={{ margin: 0, wordBreak: "break-word", paddingRight: "10px" }}>{doc.filename}</h3>
                  <button
                    onClick={(e) => handleDelete(e, doc.id)}
                    title="Delete document"
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#94a3b8",
                      fontSize: "1rem",
                      cursor: "pointer",
                      padding: "2px 6px"
                    }}
                    onMouseOver={(e) => (e.target.style.color = "#ef4444")}
                    onMouseOut={(e) => (e.target.style.color = "#94a3b8")}
                  >
                    🗑️
                  </button>
                </div>
                <div style={{ marginTop: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className={`status-badge status-${doc.status}`}>{doc.status}</span>
                  <div className="doc-date">{formatDate(doc.created_at)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}