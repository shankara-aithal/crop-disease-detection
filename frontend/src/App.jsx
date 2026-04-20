// src/App.jsx
import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { authAPI } from './api/client'

// Pages
import Home from './pages/Home'
import Result from './pages/Result'
import History from './pages/History'
import Login from './pages/Login'
import Register from './pages/Register'
import AdminDashboard from './pages/admin/Dashboard'
import AdminDataset from './pages/admin/Dataset'
import AdminTrain from './pages/admin/Train'
import AdminPredictions from './pages/admin/Predictions'

// Components
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const res = await authAPI.me()
      if (res.data.authenticated) {
        setUser(res.data.user)
      }
    } catch (err) {
      console.log('Not authenticated')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', fontSize: '18px' }}>🌿 Loading CropGuard...</div>
  }

  return (
    <BrowserRouter>
      <Navbar user={user} setUser={setUser} />
      <Toaster position="top-right" />
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/history" element={<ProtectedRoute user={user}><History /></ProtectedRoute>} />
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login setUser={setUser} />} />
        <Route path="/register" element={user ? <Navigate to="/" /> : <Register setUser={setUser} />} />

        {/* Admin routes */}
        <Route path="/admin" element={<ProtectedRoute user={user} requireAdmin={true}><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/dataset" element={<ProtectedRoute user={user} requireAdmin={true}><AdminDataset /></ProtectedRoute>} />
        <Route path="/admin/train" element={<ProtectedRoute user={user} requireAdmin={true}><AdminTrain /></ProtectedRoute>} />
        <Route path="/admin/predictions" element={<ProtectedRoute user={user} requireAdmin={true}><AdminPredictions /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
