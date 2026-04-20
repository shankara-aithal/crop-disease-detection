// src/pages/Result.jsx
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { predictionAPI } from '../api/client'
import toast from 'react-hot-toast'
import './Result.css'

export default function Result() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [pred, setPred] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResult()
  }, [id])

  const loadResult = async () => {
    try {
      const res = await predictionAPI.getResult(id)
      setPred(res.data)
    } catch (err) {
      toast.error('Failed to load result')
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="container loading">Loading result...</div>

  if (!pred) return <div className="container">Result not found</div>

  const confColor = pred.confidence >= 90 ? '#16a34a' : pred.confidence >= 75 ? '#d97706' : '#ef4444'
  const ringDeg = Math.round(pred.confidence * 3.6)

  return (
    <main className="result">
      <div className="container">
        <div className="result-header">
          <button onClick={() => navigate('/')} className="back-btn">← New Scan</button>
          <h1>Detection Result</h1>
          <span className={`badge ${pred.is_healthy ? 'healthy' : 'diseased'}`}>
            {pred.is_healthy ? '✅ Healthy' : '⚠️ Diseased'}
          </span>
        </div>

        <div className="result-grid">
          <div className="leaf-card">
            <img src={pred.image_url} alt="Leaf" />
            <div className="meta">
              🕐 {pred.created_at} · ⚡ {pred.processing_time}s
            </div>
          </div>

          <div className="result-info">
            <div className="res-card">
              <span className="res-label">Detected</span>
              <h2>{pred.disease_name}</h2>
              <p>Crop: <strong>{pred.crop_type}</strong></p>
            </div>

            <div className="res-card">
              <span className="res-label">Confidence Score</span>
              <div className="conf-display">
                <div className="conf-ring" style={{ background: `conic-gradient(${confColor} ${ringDeg}deg, #e9ecef ${ringDeg}deg)` }}>
                  <span className="conf-text">{pred.confidence}%</span>
                </div>
                <div>
                  <span className={`conf-badge ${pred.confidence >= 90 ? 'high' : pred.confidence >= 75 ? 'medium' : 'low'}`}>
                    {pred.confidence >= 90 ? 'Very High Confidence' : pred.confidence >= 75 ? 'Moderate' : 'Low — Verify Manually'}
                  </span>
                  <p>Model certainty in this prediction</p>
                </div>
              </div>
            </div>

            {pred.top3.length > 0 && (
              <div className="res-card">
                <span className="res-label">Top 3 Predictions</span>
                {pred.top3.map((p, i) => (
                  <div key={i} className="top3-row">
                    <span className="label">{i + 1}. {p.label}</span>
                    <div className="bar-wrap">
                      <div className="bar-fill" style={{ width: `${p.confidence}%` }}></div>
                    </div>
                    <span className="val">{Math.round(p.confidence)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className={`rec-card ${pred.is_healthy ? 'healthy' : 'diseased'}`}>
          <strong>Recommendation:</strong>
          <p>{pred.recommendation}</p>
        </div>

        <div className="actions">
          <button onClick={() => navigate('/')} className="btn-primary">+ Scan Another Leaf</button>
          <button onClick={() => window.print()} className="btn-secondary">🖨️ Print Report</button>
        </div>
      </div>
    </main>
  )
}
