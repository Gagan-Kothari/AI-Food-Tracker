"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { apiService } from "../services/api"
import { ShoppingBagIcon, CheckCircleIcon, SparklesIcon } from "@heroicons/react/24/outline"

interface Coupon {
  id: number
  name: string
  description: string
  points_required: number
  discount: string
  valid_until: string
  logo?: string
}

export default function Marketplace() {
  const { user } = useAuth()
  const [coupons, setCoupons] = useState<Coupon[]>([])
  const [userPoints, setUserPoints] = useState(0)
  const [loading, setLoading] = useState(true)
  const [claiming, setClaiming] = useState<number | null>(null)
  const [claimedCoupon, setClaimedCoupon] = useState<{ name: string; code: string } | null>(null)

  useEffect(() => {
    if (user?.userid) {
      fetchCoupons()
      fetchUserPoints()
    }
  }, [user?.userid])

  const fetchCoupons = async () => {
    try {
      setLoading(true)
      const response = await apiService.getCoupons()
      if (response.data && response.data.coupons) {
        setCoupons(response.data.coupons)
      }
    } catch (error) {
      console.error("Error fetching coupons:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserPoints = async () => {
    if (!user?.userid) return
    try {
      const response = await apiService.getUserPoints(user.userid)
      if (response.data.status) {
        setUserPoints(response.data.points)
      }
    } catch (error) {
      console.error("Error fetching user points:", error)
    }
  }

  const handleClaimCoupon = async (couponId: number) => {
    if (!user?.userid) return
    
    setClaiming(couponId)
    try {
      const response = await apiService.claimCoupon(user.userid, couponId)
      if (response.data.status) {
        setClaimedCoupon({
          name: response.data.coupon_name,
          code: response.data.coupon_code
        })
        // Refresh points and coupons
        await fetchUserPoints()
        await fetchCoupons()
        // Clear success message after 5 seconds
        setTimeout(() => {
          setClaimedCoupon(null)
        }, 5000)
      } else {
        alert(response.data.message || "Failed to claim coupon")
      }
    } catch (error: any) {
      console.error("Error claiming coupon:", error)
      alert(error.response?.data?.detail || "Failed to claim coupon. Please try again.")
    } finally {
      setClaiming(null)
    }
  }

  const getCouponLogo = (name: string) => {
    const logos: { [key: string]: string } = {
      blinkit: "🛒",
      zomato: "🍽️",
      instamart: "📦",
      amazon: "📦",
      zepto: "⚡"
    }
    const key = name.toLowerCase()
    return logos[key] || "🎁"
  }

  const getCouponColor = (name: string) => {
    const colors: { [key: string]: string } = {
      blinkit: "bg-green-500",
      zomato: "bg-red-500",
      instamart: "bg-blue-500",
      amazon: "bg-orange-500",
      zepto: "bg-purple-500"
    }
    const key = name.toLowerCase()
    return colors[key] || "bg-gray-500"
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-gray-200 dark:bg-gray-700 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Rewards Marketplace</h1>
            <p className="text-gray-600 dark:text-gray-400">Redeem your points for exclusive coupons and discounts</p>
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

      {claimedCoupon && (
        <div className="mb-6 bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-400 rounded-lg p-6">
          <div className="flex items-start">
            <CheckCircleIcon className="w-6 h-6 text-green-600 dark:text-green-400 mr-3 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">
                🎉 Coupon Claimed Successfully!
              </h3>
              <p className="text-green-700 dark:text-green-400 mb-3">
                Your {claimedCoupon.name} coupon code has been sent to your WhatsApp.
              </p>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-green-200 dark:border-green-800">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Coupon Code:</p>
                <p className="text-2xl font-mono font-bold text-green-600 dark:text-green-400">{claimedCoupon.code}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {coupons.map((coupon) => {
          const canAfford = userPoints >= coupon.points_required
          const isClaiming = claiming === coupon.id
          
          return (
            <div
              key={coupon.id}
              className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border-2 overflow-hidden transition-all ${
                canAfford
                  ? "border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 hover:shadow-lg"
                  : "border-gray-200 dark:border-gray-700 opacity-60"
              }`}
            >
              {/* Coupon Header */}
              <div className={`${getCouponColor(coupon.name.toLowerCase())} p-6 text-white`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-4xl">{getCouponLogo(coupon.name)}</div>
                  <div className="text-right">
                    <p className="text-sm opacity-90">Points Required</p>
                    <p className="text-2xl font-bold">{coupon.points_required}</p>
                  </div>
                </div>
                <h3 className="text-xl font-bold">{coupon.name}</h3>
              </div>

              {/* Coupon Body */}
              <div className="p-6">
                <p className="text-gray-700 dark:text-gray-300 mb-4">{coupon.description}</p>
                
                <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Discount:</span>
                  <span className="text-lg font-bold text-green-600 dark:text-green-400">{coupon.discount}</span>
                </div>

                <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Valid until: {new Date(coupon.valid_until).toLocaleDateString()}
                </div>

                <button
                  onClick={() => handleClaimCoupon(coupon.id)}
                  disabled={!canAfford || isClaiming}
                  className={`w-full py-3 px-4 rounded-lg font-semibold transition-all ${
                    canAfford
                      ? "bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white"
                      : "bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                  }`}
                >
                  {isClaiming ? (
                    <span className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Claiming...
                    </span>
                  ) : canAfford ? (
                    "Claim Coupon"
                  ) : (
                    `Need ${coupon.points_required - userPoints} more points`
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {coupons.length === 0 && (
        <div className="text-center py-12">
          <ShoppingBagIcon className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No coupons available</h2>
          <p className="text-gray-600 dark:text-gray-400">Check back later for new rewards!</p>
        </div>
      )}
    </div>
  )
}

