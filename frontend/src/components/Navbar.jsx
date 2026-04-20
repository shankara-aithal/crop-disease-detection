// src/components/Navbar.jsx
import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI, predictionAPI } from '../api/client'
import toast from 'react-hot-toast'
import './Navbar.css'

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate()
  const [alerts, setAlerts] = useState([])
  const [showAlerts, setShowAlerts] = useState(false)

  useEffect(() => {
    if (user) {
      loadAlerts()
      const interval = setInterval(loadAlerts, 30000) // Refresh every 30s
      return () => clearInterval(interval)
    }
  }, [user])

  const loadAlerts = async () => {
    try {
      const res = await predictionAPI.getAlerts()
      setAlerts(res.data.alerts || [])
    } catch (err) {
      console.error('Failed to load alerts')
    }
  }

  const handleLogout = async () => {
    try {
      await authAPI.logout()
      setUser(null)
      navigate('/')
      toast.success('Logged out')
    } catch (err) {
      toast.error('Logout failed')
    }
  }

  const handleMarkRead = async () => {
    try {
      await predictionAPI.markAlertsRead()
      await loadAlerts()
    } catch (err) {
      console.error('Failed to mark alerts as read')
    }
  }

  const unreadCount = alerts.filter(a => !a.is_read).length

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="brand">
          🌿 CropGuard<span className="accent">AI</span>
        </Link>

        <div className="nav-links">
          {user ? (
            <>
              <Link to="/">Home</Link>
              <Link to="/history">History</Link>
              {user.role === 'admin' && (
                <>
                  <Link to="/admin">Dashboard</Link>
                  <Link to="/admin/dataset">Dataset</Link>
                  <Link to="/admin/train">Train</Link>
                </>
              )}

              <div className="nav-right">
                {/* Alerts Bell */}
                {unreadCount > 0 && (
                  <div className="alerts-bell">
                    <button onClick={() => setShowAlerts(!showAlerts)}>
                      🔔 <span className="badge">{unreadCount}</span>
                    </button>
                    {showAlerts && (
                      <div className="alerts-dropdown">
                        <div className="alerts-header">
                          <h4>Notifications ({unreadCount} new)</h4>
                          <button onClick={handleMarkRead} className="btn-link">Mark all read</button>
                        </div>
                        <div className="alerts-list">
                          {alerts.slice(0, 5).map(a => (
                            <Link key={a.id} to={`/result/${a.prediction_id}`} className="alert-item">
                              <span>{a.message}</span>
                              <small>{new Date(a.created_at).toLocaleString()}</small>
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* User Menu */}
                <div className="user-menu">
                  <span>{user.username}</span>
                  <button onClick={handleLogout} className="btn-logout">Logout</button>
                </div>
              </div>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register" className="btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
