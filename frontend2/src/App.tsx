"use client"

import type React from "react"

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthContext"
import { AdminProvider, useAdmin } from "./contexts/AdminContext"
import { useAuth } from "./contexts/AuthContext"
import Navbar from "./components/Navbar"
import Footer from "./components/Footer"
import Login from "./pages/Login"
import AdminLogin from "./pages/AdminLogin"
import AdminDashboard from "./pages/AdminDashboard"
import Signup from "./pages/Signup"
import Dashboard from "./pages/Dashboard"
import Scan from "./pages/Scan"
import Inventory from "./pages/Inventory"
import Donate from "./pages/Donate"
import Recipes from "./pages/Recipes"
import Groceries from "./pages/Groceries"
import "./App.css"

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    )
  }

  return user ? <>{children}</> : <Navigate to="/login" />
}

function AppContent() {
  const { user } = useAuth()
  const { admin } = useAdmin()

  return (
    <div className="min-h-screen bg-gray-50">
      {user && !admin && <Navbar />}
      <main className={user && !admin ? "pt-16" : ""}>
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
          <Route path="/admin/login" element={admin ? <Navigate to="/admin" /> : <AdminLogin />} />
          <Route path="/admin" element={admin ? <AdminDashboard /> : <Navigate to="/admin/login" />} />
          <Route path="/signup" element={user ? <Navigate to="/dashboard" /> : <Signup />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scan"
            element={
              <ProtectedRoute>
                <Scan />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory"
            element={
              <ProtectedRoute>
                <Inventory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/donate"
            element={
              <ProtectedRoute>
                <Donate />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recipes"
            element={
              <ProtectedRoute>
                <Recipes />
              </ProtectedRoute>
            }
          />
          <Route
            path="/groceries"
            element={
              <ProtectedRoute>
                <Groceries />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to={user ? "/dashboard" : admin ? "/admin" : "/login"} />} />
        </Routes>
      </main>
      {user && !admin && <Footer />}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AdminProvider>
        <Router>
          <AppContent />
        </Router>
      </AdminProvider>
    </AuthProvider>
  )
}

export default App
