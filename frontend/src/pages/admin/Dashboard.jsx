// src/pages/admin/Dashboard.jsx
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { adminAPI } from '../../api/client'
import toast from 'react-hot-toast'
import '../styles/Admin.css'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
    const interval = setInterval(loadDashboard, 60000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboard = async () => {
    try {
      const res = await adminAPI.getDashboard()
      setDashboard(res.data)
    } catch (err) {
      toast.error('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading || !dashboard) return <div className="loading">Loading dashboard...</div>

  const { metrics, trend, disease_counts, recent, active_model } = dashboard

  const chartData = {
    labels: trend.map(t => t.date),
    datasets: [
      {
        label: 'Healthy',
        data: trend.map(t => t.healthy),
        backgroundColor: '#86efac',
        borderRadius: 4,
      },
      {
        label: 'Diseased',
        data: trend.map(t => t.diseased),
        backgroundColor: '#fca5a5',
        borderRadius: 4,
      },
    ],
  }

  return (
    <main className="admin">
      <div className="container">
        <div className="admin-header">
          <div>
            <h1>Admin Dashboard</h1>
            <p>System monitoring & management</p>
          </div>
          <div className="admin-buttons">
            <Link to="/admin/dataset" className="btn-secondary">📁 Dataset</Link>
            <Link to="/admin/train" className="btn-secondary">⚙️ Train Model</Link>
          </div>
        </div>

        {/* Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <p className="label">Total Predictions</p>
            <p className="value">{metrics.total}</p>
            <p className="sub">+{metrics.today} today</p>
          </div>
          <div className="metric-card">
            <p className="label">Diseased</p>
            <p className="value" style={{ color: '#dc2626' }}>{metrics.diseased}</p>
            <p className="sub">{Math.round(metrics.diseased / metrics.total * 100)}% rate</p>
          </div>
          <div className="metric-card">
            <p className="label">Avg Confidence</p>
            <p className="value">{metrics.avg_confidence}%</p>
            <p className="sub">model certainty</p>
          </div>
          <div className="metric-card">
            <p className="label">Active Users</p>
            <p className="value">{metrics.users}</p>
            <p className="sub">registered</p>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="chart-card">
            <h3>Daily Predictions (7 days)</h3>
            <div style={{ height: '200px' }}>
              <Bar data={chartData} options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: { y: { beginAtZero: true } }
              }} />
            </div>
          </div>

          <div className="chart-card">
            <h3>Disease Breakdown</h3>
            <div className="disease-list">
              {disease_counts.map((d, i) => (
                <div key={i} className="disease-row">
                  <span className="name">{d.name}</span>
                  <span className="count">{d.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Active Model */}
        {active_model && (
          <div className="model-card">
            <h3>Active Model</h3>
            <div className="model-info">
              <p><strong>Version:</strong> {active_model.model_version}</p>
              <p><strong>Val Accuracy:</strong> {active_model.val_accuracy}%</p>
              <p><strong>Epochs:</strong> {active_model.epochs}</p>
              <p><strong>Trained:</strong> {active_model.trained_at}</p>
            </div>
          </div>
        )}

        {/* Recent Predictions */}
        <div className="recent-card">
          <div className="card-header">
            <h3>Recent Predictions</h3>
            <Link to="/admin/predictions" className="btn-link">View All →</Link>
          </div>
          <table className="pred-table">
            <thead>
              <tr>
                <th>ID</th><th>Crop</th><th>Result</th><th>Confidence</th><th>Time</th>
              </tr>
            </thead>
            <tbody>
              {recent.map(p => (
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td>{p.crop_type}</td>
                  <td>
                    <span className={`badge ${p.is_healthy ? 'h' : 'd'}`}>
                      {p.is_healthy ? 'Healthy' : p.disease_name.slice(0, 20)}
                    </span>
                  </td>
                  <td>
                    <div className="conf-bar">
                      <div style={{ width: `${p.confidence}%` }}></div>
                    </div>
                    {p.confidence}%
                  </td>
                  <td className="time">{p.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}
