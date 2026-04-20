// src/pages/History.jsx
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { predictionAPI } from '../api/client'
import toast from 'react-hot-toast'
import './History.css'

export default function History() {
  const [preds, setPreds] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const res = await predictionAPI.getHistory()
      setPreds(res.data)
    } catch (err) {
      toast.error('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="container loading">Loading history...</div>

  const healthy = preds.filter(p => p.is_healthy).length
  const diseased = preds.filter(p => !p.is_healthy).length

  return (
    <main className="history">
      <div className="container">
        <div className="history-header">
          <div>
            <h1>My Scan History</h1>
            <p>{preds.length} total scans</p>
          </div>
          <Link to="/" className="btn-primary">+ New Scan</Link>
        </div>

        {preds.length > 0 && (
          <div className="stats-row">
            <span className="stat">✅ <strong>{healthy}</strong> Healthy</span>
            <span className="stat">⚠️ <strong>{diseased}</strong> Diseased</span>
          </div>
        )}

        {preds.length === 0 ? (
          <div className="empty-state">
            <span className="emoji">🌿</span>
            <h2>No scans yet</h2>
            <p>Upload your first leaf image to get started.</p>
            <Link to="/" className="btn-primary">Start Scanning</Link>
          </div>
        ) : (
          <div className="history-grid">
            {preds.map(p => (
              <Link key={p.id} to={`/result/${p.id}`} className={`history-card ${p.is_healthy ? 'healthy' : 'diseased'}`}>
                <img src={p.image_url} alt="leaf" />
                <div className="content">
                  <div className="header">
                    <span className={`badge ${p.is_healthy ? 'h' : 'd'}`}>
                      {p.is_healthy ? '✅' : '⚠️'}
                    </span>
                    <span className="time">{p.created_at}</span>
                  </div>
                  <p className="disease">{p.disease_name}</p>
                  <p className="meta">{p.crop_type} · {p.confidence}% confidence</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
