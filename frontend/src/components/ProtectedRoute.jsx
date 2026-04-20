// src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ user, requireAdmin = false, children }) {
  if (!user) {
    return <Navigate to="/login" />
  }

  if (requireAdmin && user.role !== 'admin') {
    return <Navigate to="/" />
  }

  return children
}
