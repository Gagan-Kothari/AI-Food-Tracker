"use client"

import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { apiService } from "../services/api"
import {
  CameraIcon,
  CubeIcon,
  HeartIcon,
  BookOpenIcon,
  ShoppingCartIcon,
  ShoppingBagIcon,
  SparklesIcon,
  ArrowRightIcon,
} from "@heroicons/react/24/outline"

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    items_donated: 0,
    recipes_tried: 0,
    items_scanned: 0,
  })
  const [userPoints, setUserPoints] = useState(0)
  const [loading, setLoading] = useState(true)

  const featureCards = [
    {
      title: "Scan Item",
      description: "Add items to your inventory by scanning barcodes",
      icon: CameraIcon,
      path: "/scan",
      color: "bg-blue-500",
      emoji: "📷",
    },
    {
      title: "My Inventory",
      description: "View and manage all your food items",
      icon: CubeIcon,
      path: "/inventory",
      color: "bg-green-500",
      emoji: "📦",
    },
    {
      title: "Donate Items",
      description: "Donate expiring items to local NGOs",
      icon: HeartIcon,
      path: "/donate",
      color: "bg-red-500",
      emoji: "❤️",
    },
    {
      title: "Suggested Recipes",
      description: "Get AI-powered recipe suggestions",
      icon: BookOpenIcon,
      path: "/recipes",
      color: "bg-purple-500",
      emoji: "🍳",
    },
    {
      title: "Grocery Suggestions",
      description: "Smart recommendations for your next shopping",
      icon: ShoppingCartIcon,
      path: "/groceries",
      color: "bg-orange-500",
      emoji: "🛒",
    },
    {
      title: "Marketplace",
      description: "Redeem your points for exclusive coupons",
      icon: ShoppingBagIcon,
      path: "/marketplace",
      color: "bg-indigo-500",
      emoji: "🎁",
    },
  ]

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.userid) {
        setLoading(false)
        return
      }

      try {
        // Fetch dashboard stats
        const statsResponse = await apiService.getDashboardStats(user.userid)
        if (statsResponse.data.status) {
          setStats({
            items_donated: statsResponse.data.items_donated || 0,
            recipes_tried: statsResponse.data.recipes_tried || 0,
            items_scanned: statsResponse.data.items_scanned || 0,
          })
        }

        // Fetch user points
        const pointsResponse = await apiService.getUserPoints(user.userid)
        if (pointsResponse.data.status) {
          setUserPoints(pointsResponse.data.points || 0)
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [user?.userid])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Welcome back, {user?.username}! 👋
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your food inventory and reduce waste with smart tracking.
            </p>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg px-6 py-4">
            <div className="flex items-center gap-2">
              <SparklesIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Your Points</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">{userPoints}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border-2 border-gray-200 dark:border-gray-700 overflow-hidden transition-all hover:border-green-500 dark:hover:border-green-500 hover:shadow-lg">
          <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 text-white">
            <div className="flex items-center justify-between mb-2">
              <div className="text-4xl">❤️</div>
              <div className="text-right">
                <p className="text-sm opacity-90">Items Donated</p>
                <p className="text-3xl font-bold">{stats.items_donated}</p>
              </div>
            </div>
            <p className="text-green-100 text-sm">Items donated to NGOs</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border-2 border-gray-200 dark:border-gray-700 overflow-hidden transition-all hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white">
            <div className="flex items-center justify-between mb-2">
              <div className="text-4xl">📱</div>
              <div className="text-right">
                <p className="text-sm opacity-90">Items Scanned</p>
                <p className="text-3xl font-bold">{stats.items_scanned}</p>
              </div>
            </div>
            <p className="text-blue-100 text-sm">Total items in your inventory</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border-2 border-gray-200 dark:border-gray-700 overflow-hidden transition-all hover:border-purple-500 dark:hover:border-purple-500 hover:shadow-lg">
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 text-white">
            <div className="flex items-center justify-between mb-2">
              <div className="text-4xl">🍳</div>
              <div className="text-right">
                <p className="text-sm opacity-90">Recipes Tried</p>
                <p className="text-3xl font-bold">{stats.recipes_tried}</p>
              </div>
            </div>
            <p className="text-purple-100 text-sm">AI-suggested recipes used</p>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featureCards.map((card) => {
          return (
            <Link key={card.title} to={card.path} className="group block">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border-2 border-gray-200 dark:border-gray-700 overflow-hidden transition-all hover:border-green-500 dark:hover:border-green-500 hover:shadow-lg">
                {/* Card Header */}
                <div className={`${card.color} p-6 text-white`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-4xl">{card.emoji}</div>
                    <ArrowRightIcon className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <h3 className="text-xl font-bold">{card.title}</h3>
                </div>

                {/* Card Body */}
                <div className="p-6">
                  <p className="text-gray-700 dark:text-gray-300">{card.description}</p>
                  <div className="mt-4 flex items-center text-sm font-medium text-green-600 dark:text-green-400 group-hover:underline">
                    Get started
                    <ArrowRightIcon className="w-4 h-4 ml-1" />
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
