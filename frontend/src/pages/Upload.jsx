import { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"
import { API_BASE_URL } from "../api/config"

export default function Upload() {
  const [activeTab, setActiveTab] = useState("paste") // "paste" | "file"
  const [filename, setFilename] = useState("")
  const [content, setContent] = useState("")
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const { token } = useAuth()
  const navigate = useNavigate()

  const handlePasteSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const response = await axios.post(
        `${API_BASE_URL}/documents/`,
        { filename, content },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      navigate(`/results/${response.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed")
    } finally {
      setLoading(false)
    }
  }

  const handleFileSubmit = async (e) => {
    e.preventDefault()
    if (!selectedFile) {
      setError("Please select a file to upload")
      return
    }
    setError("")
    setLoading(true)

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      // Note: Do NOT set Content-Type manually here so browser/axios attaches the boundary parameter
      const response = await axios.post(
        `${API_BASE_URL}/documents/upload-file`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      navigate(`/results/${response.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || "File upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="container page">
        <div className="page-header">
          <h1>Upload Document</h1>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
          <button
            className={`btn ${activeTab === "paste" ? "" : "btn-small"}`}
            style={{
              background: activeTab === "paste" ? "#2563eb" : "#f1f5f9",
              color: activeTab === "paste" ? "#ffffff" : "#475569",
              border: "1px solid #cbd5e1"
            }}
            onClick={() => setActiveTab("paste")}
          >
            ✍️ Paste Text
          </button>
          <button
            className={`btn ${activeTab === "file" ? "" : "btn-small"}`}
            style={{
              background: activeTab === "file" ? "#2563eb" : "#f1f5f9",
              color: activeTab === "file" ? "#ffffff" : "#475569",
              border: "1px solid #cbd5e1"
            }}
            onClick={() => setActiveTab("file")}
          >
            📁 Upload File (.txt, .pdf, .md)
          </button>
        </div>

        {error && <div className="error-msg">{error}</div>}

        {activeTab === "paste" ? (
          <form onSubmit={handlePasteSubmit} style={{ maxWidth: "700px" }}>
            <div className="form-group">
              <label>Document Name</label>
              <input
                type="text"
                placeholder="e.g. quarterly_report.txt"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Document Content</label>
              <textarea
                placeholder="Paste your document text here..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
                style={{ minHeight: "220px" }}
              />
            </div>
            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Uploading & Analysing..." : "Upload & Analyse"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleFileSubmit} style={{ maxWidth: "700px" }}>
            <div className="form-group">
              <label>Select Document File</label>
              <input
                type="file"
                accept=".txt,.pdf,.md,.csv,.json,.doc,.docx"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                required
                style={{
                  padding: "10px",
                  border: "1px dashed #cbd5e1",
                  borderRadius: "8px",
                  width: "100%",
                  background: "#f8fafc"
                }}
              />
              <span style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "6px", display: "block" }}>
                Supported formats: .txt, .pdf, .md, .csv, .json
              </span>
            </div>
            <button className="btn" type="submit" disabled={loading || !selectedFile}>
              {loading ? "Parsing & Analysing..." : "Upload & Analyse File"}
            </button>
          </form>
        )}
      </div>
    </>
  )
}