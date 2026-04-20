// src/pages/Login.jsx
import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'
import './Auth.css'

export default function Login({ setUser }) {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', password: '', remember: false })

  const handleChange = e => {
    const { name, type, checked, value } = e.target
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authAPI.login(form.username, form.password, form.remember)
      setUser(res.data.user)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <span className="emoji">🌿</span>
          <h1>Welcome Back</h1>
          <p>Sign in to CropGuard AI</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Enter your username"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          <label className="remember">
            <input
              type="checkbox"
              name="remember"
              checked={form.remember}
              onChange={handleChange}
            />
            Remember me
          </label>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="auth-divider">OR</div>

        <p className="auth-link">
          Don't have an account? <Link to="/register">Register here</Link>
        </p>

        <div className="demo-box">
          <strong>Demo Admin:</strong><br/>
          Username: <code>admin</code><br/>
          Password: <code>Admin@123</code>
        </div>
      </div>
    </div>
  )
}
