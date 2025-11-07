"use client"

import type React from "react"

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthContext"
import { useAuth } from "./contexts/AuthContext"
import { DarkModeProvider } from "./contexts/DarkModeContext"
import Navbar from "./components/Navbar"
import Footer from "./components/Footer"
import Login from "./pages/Login"
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
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500 dark:border-green-400"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" />
  }

  if (user.isAdmin) {
    return <Navigate to="/admin" />
  }

  return <>{children}</>
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500 dark:border-green-400"></div>
      </div>
    )
  }

  return user && user.isAdmin ? <>{children}</> : <Navigate to="/login" />
}

function AppContent() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {user && !user.isAdmin && <Navbar />}
      <main className={user && !user.isAdmin ? "pt-16" : ""}>
        <Routes>
          <Route path="/login" element={user ? (user.isAdmin ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />) : <Login />} />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
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
          <Route path="/" element={<Navigate to={user ? (user.isAdmin ? "/admin" : "/dashboard") : "/login"} />} />
        </Routes>
      </main>
      {user && !user.isAdmin && <Footer />}
    </div>
  )
}

function App() {
  return (
    <DarkModeProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </DarkModeProvider>
  )
}

export default App
