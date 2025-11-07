"use client"

import { useState, useEffect } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useDarkMode } from "../contexts/DarkModeContext"
import { apiService } from "../services/api"
import {
  HomeIcon,
  CubeIcon,
  CameraIcon,
  HeartIcon,
  BookOpenIcon,
  ShoppingCartIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  SunIcon,
  MoonIcon,
} from "@heroicons/react/24/outline"

export default function Navbar() {
  const { user, logout } = useAuth()
  const { darkMode, toggleDarkMode } = useDarkMode()
  const location = useLocation()
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [userPoints, setUserPoints] = useState(0)

  useEffect(() => {
    if (user?.userid) {
      fetchUserPoints()
    }
  }, [user?.userid])

  const fetchUserPoints = async () => {
    try {
      const response = await apiService.getUserPoints(user!.userid)
      if (response.data.status) {
        setUserPoints(response.data.points)
      }
    } catch (error) {
      console.error("Error fetching user points:", error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: HomeIcon },
    { name: "Inventory", path: "/inventory", icon: CubeIcon },
    { name: "Scan Item", path: "/scan", icon: CameraIcon },
    { name: "Donate", path: "/donate", icon: HeartIcon },
    { name: "Recipes", path: "/recipes", icon: BookOpenIcon },
    { name: "Groceries", path: "/groceries", icon: ShoppingCartIcon },
  ]

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-lg fixed top-0 left-0 right-0 z-50 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-500 dark:bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🍎</span>
              </div>
              <span className="text-xl font-bold text-gray-800 dark:text-white">FoodTracker</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30"
                      : "text-gray-600 dark:text-gray-300 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="relative p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 border border-transparent hover:border-gray-300 dark:hover:border-gray-600"
              aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {darkMode ? (
                <SunIcon className="w-5 h-5 text-yellow-500" />
              ) : (
                <MoonIcon className="w-5 h-5" />
              )}
            </button>
            {/* Points Display */}
            <div className="flex items-center space-x-2 bg-yellow-100 dark:bg-yellow-900/30 px-3 py-2 rounded-lg">
              <span className="text-yellow-600 dark:text-yellow-400 text-lg">🪙</span>
              <span className="text-sm font-semibold text-yellow-800 dark:text-yellow-300">{userPoints} points</span>
            </div>
            <div className="flex items-center space-x-2">
              <UserIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              <span className="text-sm text-gray-700 dark:text-gray-300">Hi, {user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 dark:bg-red-600 hover:bg-red-600 dark:hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 border border-transparent hover:border-gray-300 dark:hover:border-gray-600"
              aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {darkMode ? (
                <SunIcon className="w-5 h-5 text-yellow-500" />
              ) : (
                <MoonIcon className="w-5 h-5" />
              )}
            </button>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white focus:outline-none"
            >
              {isMenuOpen ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium ${
                    location.pathname === item.path
                      ? "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30"
                      : "text-gray-600 dark:text-gray-300 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              {/* Dark Mode Toggle for Mobile Menu */}
              <button
                onClick={toggleDarkMode}
                className="w-full flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md font-medium transition-colors mb-2 mx-3"
              >
                {darkMode ? (
                  <>
                    <SunIcon className="w-5 h-5 text-yellow-500" />
                    <span>Switch to Light Mode</span>
                  </>
                ) : (
                  <>
                    <MoonIcon className="w-5 h-5" />
                    <span>Switch to Dark Mode</span>
                  </>
                )}
              </button>
              {/* Points Display for Mobile */}
              <div className="flex items-center space-x-2 px-3 py-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg mx-3 mb-2">
                <span className="text-yellow-600 dark:text-yellow-400 text-lg">🪙</span>
                <span className="text-sm font-semibold text-yellow-800 dark:text-yellow-300">{userPoints} points</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-2">
                <UserIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Hi, {user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
