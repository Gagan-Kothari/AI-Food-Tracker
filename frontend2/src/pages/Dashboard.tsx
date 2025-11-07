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
  ChevronRightIcon,
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
      color: "bg-blue-500",
      hoverColor: "hover:bg-blue-600",
    },
    {
      title: "My Inventory",
      description: "View and manage all your food items",
      icon: CubeIcon,
      path: "/inventory",
      color: "bg-green-500",
      hoverColor: "hover:bg-green-600",
    },
    {
      title: "Donate Items",
      description: "Donate expiring items to local NGOs",
      icon: HeartIcon,
      path: "/donate",
      color: "bg-red-500",
      hoverColor: "hover:bg-red-600",
    },
    {
      title: "Suggested Recipes",
      description: "Get AI-powered recipe suggestions",
      icon: BookOpenIcon,
      path: "/recipes",
      color: "bg-purple-500",
      hoverColor: "hover:bg-purple-600",
    },
    {
      title: "Grocery Suggestions",
      description: "Smart recommendations for your next shopping",
      icon: ShoppingCartIcon,
      path: "/groceries",
      color: "bg-orange-500",
      hoverColor: "hover:bg-orange-600",
    },
  ]

  useEffect(() => {
    const fetchStats = async () => {
      if (!user?.userid) {
        setLoading(false)
        return
      }

      try {
        const response = await apiService.getDashboardStats(user.userid)
        if (response.data.status) {
          setStats({
            items_donated: response.data.items_donated || 0,
            recipes_tried: response.data.recipes_tried || 0,
            items_scanned: response.data.items_scanned || 0,
          })
        }
      } catch (error) {
        console.error("Error fetching dashboard stats:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [user?.userid])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Welcome back, {user?.username}! 👋</h1>
        <p className="text-gray-600 dark:text-gray-400">Manage your food inventory and reduce waste with smart tracking.</p>
      </div>



      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featureCards.map((card) => {
          const Icon = card.icon
          return (
            <Link key={card.title} to={card.path} className="group block">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6 border border-gray-100 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${card.color} ${card.hoverColor} transition-colors`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <ChevronRightIcon className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400 transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{card.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">{card.description}</p>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Quick Stats */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-green-400 to-green-600 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Items Donated</h3>
          <p className="text-3xl font-bold">{loading ? "..." : stats.items_donated}</p>
          <p className="text-green-100 text-sm">Items donated to NGOs</p>
        </div>
        <div className="bg-gradient-to-r from-blue-400 to-blue-600 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Items Scanned</h3>
          <p className="text-3xl font-bold">{loading ? "..." : stats.items_scanned}</p>
          <p className="text-blue-100 text-sm">Total items in your inventory</p>
        </div>
        <div className="bg-gradient-to-r from-purple-400 to-purple-600 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Recipes Tried</h3>
          <p className="text-3xl font-bold">{loading ? "..." : stats.recipes_tried}</p>
          <p className="text-purple-100 text-sm">AI-suggested recipes used</p>
        </div>
      </div>
    </div>
  )
}
