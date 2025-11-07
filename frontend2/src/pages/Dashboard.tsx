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
  ArrowRightIcon,
} from "@heroicons/react/24/outline"

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    items_donated: 0,
    recipes_tried: 0,
    items_scanned: 0,
  })
  const [loading, setLoading] = useState(true)

  const featureCards = [
    {
      title: "Scan Item",
      description: "Add items to your inventory by scanning barcodes",
      icon: CameraIcon,
      path: "/scan",
      color: "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400",
      emoji: "📷",
    },
    {
      title: "My Inventory",
      description: "View and manage all your food items",
      icon: CubeIcon,
      path: "/inventory",
      color: "bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400",
      emoji: "📦",
    },
    {
      title: "Donate Items",
      description: "Donate expiring items to local NGOs",
      icon: HeartIcon,
      path: "/donate",
      color: "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400",
      emoji: "❤️",
    },
    {
      title: "Suggested Recipes",
      description: "Get AI-powered recipe suggestions",
      icon: BookOpenIcon,
      path: "/recipes",
      color: "bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400",
      emoji: "🍳",
    },
    {
      title: "Grocery Suggestions",
      description: "Smart recommendations for your next shopping",
      icon: ShoppingCartIcon,
      path: "/groceries",
      color: "bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400",
      emoji: "🛒",
    },
    {
      title: "Marketplace",
      description: "Redeem your points for exclusive coupons",
      icon: ShoppingBagIcon,
      path: "/marketplace",
      color: "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400",
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back, {user?.username}! 👋
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your food inventory and reduce waste with smart tracking.
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-all hover:shadow-md h-full flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="text-2xl">❤️</div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Items Donated</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.items_donated}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-auto">Items donated to NGOs</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-all hover:shadow-md h-full flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="text-2xl">📱</div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Items Scanned</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.items_scanned}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-auto">Total items in your inventory</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-all hover:shadow-md h-full flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="text-2xl">🍳</div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">Recipes Tried</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.recipes_tried}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-auto">AI-suggested recipes used</p>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featureCards.map((card) => {
          return (
            <Link key={card.title} to={card.path} className="group block h-full">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-all hover:shadow-md h-full flex flex-col">
                {/* Card Header */}
                <div className={`${card.color} p-4 border-b border-gray-200 dark:border-gray-700`}>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl">{card.emoji}</div>
                    <ArrowRightIcon className={`w-4 h-4 ${card.color.split(' ')[2]} opacity-0 group-hover:opacity-100 transition-opacity`} />
                  </div>
                  <h3 className="text-lg font-semibold mt-2">{card.title}</h3>
                </div>

                {/* Card Body */}
                <div className="p-4 flex-1 flex flex-col">
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 flex-1">{card.description}</p>
                  <div className="flex items-center text-xs font-medium text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors">
                    Get started
                    <ArrowRightIcon className="w-3 h-3 ml-1" />
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
