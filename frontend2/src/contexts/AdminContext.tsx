"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { apiService } from "../services/api"

interface AdminSession {
  token: string
}

interface AdminContextType {
  admin: AdminSession | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  loading: boolean
}

const AdminContext = createContext<AdminContextType | undefined>(undefined)

export function AdminProvider({ children }: { children: React.ReactNode }) {
  const [admin, setAdmin] = useState<AdminSession | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const saved = localStorage.getItem("adminSession")
    if (saved) {
      setAdmin(JSON.parse(saved))
    }
    setLoading(false)
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const res = await apiService.adminLogin(username, password)
      if (res.data?.token) {
        const session = { token: res.data.token as string }
        setAdmin(session)
        localStorage.setItem("adminSession", JSON.stringify(session))
        return true
      }
      return false
    } catch (e) {
      return false
    }
  }

  const logout = () => {
    setAdmin(null)
    localStorage.removeItem("adminSession")
  }

  return (
    <AdminContext.Provider value={{ admin, login, logout, loading }}>
      {children}
    </AdminContext.Provider>
  )
}

export function useAdmin() {
  const ctx = useContext(AdminContext)
  if (!ctx) throw new Error("useAdmin must be used within an AdminProvider")
  return ctx
}


