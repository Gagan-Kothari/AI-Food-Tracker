"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { apiService } from "../services/api"
import { HeartIcon, CheckCircleIcon } from "@heroicons/react/24/outline"

interface DonationItem {
  inventory_id: number
  f_name: string
  brands: string
  quantity: string
  expiry_date: string
  selected: boolean
}

interface NGO {
  id: number
  name: string
  address: string
  contact: string
  description: string
}

export default function Donate() {
  const { user } = useAuth()
  const [eligibleItems, setEligibleItems] = useState<DonationItem[]>([])
  const [selectedNGO, setSelectedNGO] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [donating, setDonating] = useState(false)
  const [success, setSuccess] = useState(false)
  const [pointsEarned, setPointsEarned] = useState(0)
  const [totalPoints, setTotalPoints] = useState(0)
  const [redirectCountdown, setRedirectCountdown] = useState(3)
  const [error, setError] = useState<string | null>(null)

  // Mock NGO data - in real app, this would come from your backend
  const ngos: NGO[] = [
    {
      id: 1,
      name: "Food Bank Central",
      address: "123 Main St, City",
      contact: "+1 234-567-8900",
      description: "Helping families in need with fresh food donations",
    },
    {
      id: 2,
      name: "Community Kitchen",
      address: "456 Oak Ave, City",
      contact: "+1 234-567-8901",
      description: "Providing meals to homeless and low-income individuals",
    },
    {
      id: 3,
      name: "Shelter Support Network",
      address: "789 Pine St, City",
      contact: "+1 234-567-8902",
      description: "Supporting local shelters with food and supplies",
    },
  ]

  useEffect(() => {
    fetchEligibleItems()
  }, [])

  const fetchEligibleItems = async () => {
    if (!user?.userid) return

    try {
      // Get items expiring within 7 days
      const response = await apiService.getInventory(user.userid)
      if (Array.isArray(response.data)) {
        const sevenDaysFromNow = new Date()
        sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7)

        const eligible = response.data
          .filter((item) => {
            const expiryDate = new Date(item.expiry_date)
            const today = new Date()
            return expiryDate > today && expiryDate <= sevenDaysFromNow
          })
          .map((item) => ({ ...item, selected: false }))

        setEligibleItems(eligible)
      }
    } catch (error) {
      console.error("Error fetching eligible items:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleItemSelection = (inventoryId: number) => {
    setEligibleItems((items) =>
      items.map((item) => (item.inventory_id === inventoryId ? { ...item, selected: !item.selected } : item)),
    )
  }

  const handleDonate = async () => {
    const selectedItems = eligibleItems.filter((item) => item.selected)

    if (selectedItems.length === 0 || !selectedNGO) {
      setError("Please select items and an NGO to donate to")
      return
    }

    setDonating(true)

    try {
      const inventoryIds = selectedItems.map((item) => item.inventory_id)
      const response = await apiService.donateItems(inventoryIds, user!.userid)
      
      if (response.data.status) {
        // Show points earned
        const earnedPoints = response.data.points_earned
        const totalPointsValue = response.data.total_points
        
        setPointsEarned(earnedPoints)
        setTotalPoints(totalPointsValue)
        setSuccess(true)
        
        // Start countdown for redirect
        let countdown = 3
        const countdownInterval = setInterval(() => {
          countdown -= 1
          setRedirectCountdown(countdown)
          
          if (countdown <= 0) {
            clearInterval(countdownInterval)
            // Refresh the eligible items list
            fetchEligibleItems()
            // Trigger a page reload to update navbar points
            window.location.reload()
          }
        }, 1000)
      } else {
        setError("Failed to donate items: " + response.data.message)
      }
    } catch (error) {
      console.error("Error donating items:", error)
      setError("Failed to donate items. Please try again.")
    } finally {
      setDonating(false)
      // Reset selections
      setEligibleItems((items) => items.map((item) => ({ ...item, selected: false })))
      setSelectedNGO(null)
    }
  }

  

  const getDaysUntilExpiry = (expiryDate: string) => {
    const expiry = new Date(expiryDate)
    const today = new Date()
    const diffTime = expiry.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500 mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Donation Successful! 🎉</h1>
          <p className="text-gray-600 mb-6">Thank you for helping reduce food waste and supporting your community.</p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-green-800 mb-2">You've earned {pointsEarned} points!</h2>
            <p className="text-green-700">Your total points: {totalPoints}</p>
            <p className="text-green-700 mt-2">Your donation helps feed families in need and reduces food waste.</p>
          </div>
          <div className="text-blue-600 font-medium">
            Redirecting in {redirectCountdown} seconds...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Donate Items</h1>
        <p className="text-gray-600">Help reduce food waste by donating items that are expiring soon</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
            <div className="ml-auto pl-3">
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600"
              >
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {eligibleItems.length === 0 ? (
        <div className="text-center py-12">
          <HeartIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No items available for donation</h2>
          <p className="text-gray-600">Items expiring within the next 7 days will appear here for donation</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Eligible Items */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Items Available for Donation</h2>
            <div className="space-y-4">
              {eligibleItems.map((item) => (
                <div
                  key={item.inventory_id}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    item.selected ? "border-green-500 bg-green-50" : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => toggleItemSelection(item.inventory_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{item.f_name}</h3>
                      <p className="text-sm text-gray-600">{item.brands}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm">
                        <span className="text-gray-600">Qty: {item.quantity}</span>
                        <span className="text-orange-600">Expires in {getDaysUntilExpiry(item.expiry_date)} days</span>
                      </div>
                    </div>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        item.selected ? "border-green-500 bg-green-500" : "border-gray-300"
                      }`}
                    >
                      {item.selected && <CheckCircleIcon className="w-3 h-3 text-white" />}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* NGO Selection */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Select NGO</h2>
            <div className="space-y-4">
              {ngos.map((ngo) => (
                <div
                  key={ngo.id}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    selectedNGO === ngo.id ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedNGO(ngo.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{ngo.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{ngo.description}</p>
                      <div className="mt-2 text-sm text-gray-500">
                        <p>{ngo.address}</p>
                        <p>{ngo.contact}</p>
                      </div>
                    </div>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedNGO === ngo.id ? "border-blue-500 bg-blue-500" : "border-gray-300"
                      }`}
                    >
                      {selectedNGO === ngo.id && <CheckCircleIcon className="w-3 h-3 text-white" />}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Donate Button */}
            <div className="mt-6">
              <button
                onClick={handleDonate}
                disabled={donating || eligibleItems.filter((item) => item.selected).length === 0 || !selectedNGO}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center"
              >
                {donating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing Donation...
                  </>
                ) : (
                  <>
                    <HeartIcon className="w-5 h-5 mr-2" />
                    Donate Selected Items
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
