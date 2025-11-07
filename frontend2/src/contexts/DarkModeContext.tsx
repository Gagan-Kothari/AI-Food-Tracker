"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

interface DarkModeContextType {
  darkMode: boolean
  toggleDarkMode: () => void
}

const DarkModeContext = createContext<DarkModeContextType | undefined>(undefined)

export function DarkModeProvider({ children }: { children: React.ReactNode }) {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem("darkMode")
    if (saved !== null) {
      return saved === "true"
    }
    // Check system preference
    return window.matchMedia("(prefers-color-scheme: dark)").matches
  })

  useEffect(() => {
    // Apply dark mode class to document
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
    // Save to localStorage
    localStorage.setItem("darkMode", darkMode.toString())
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode((prev) => !prev)
  }

  return (
    <DarkModeContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </DarkModeContext.Provider>
  )
}

export function useDarkMode() {
  const context = useContext(DarkModeContext)
  if (context === undefined) {
    throw new Error("useDarkMode must be used within a DarkModeProvider")
  }
  return context
}

