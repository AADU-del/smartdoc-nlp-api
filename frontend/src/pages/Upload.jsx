import { useState } from "react"
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
}