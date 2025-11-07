"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useDarkMode } from "../contexts/DarkModeContext"
import { apiService } from "../services/api"
import { ShoppingCartIcon, PlusIcon, MinusIcon, DocumentArrowDownIcon, CheckIcon, ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline"

interface GroceryItem {
  id: number
  name: string
  category: string
  suggested: boolean
  quantity: number
  unit: string
  priority: "high" | "medium" | "low"
  reason: string
  confidence?: number
}

export default function Groceries() {
  const { user } = useAuth()
  const { darkMode } = useDarkMode()
  const [groceryList, setGroceryList] = useState<GroceryItem[]>([])
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    generateGrocerySuggestions()
  }, [])

  const generateGrocerySuggestions = async () => {
    if (!user?.userid) return

    try {
      setLoading(true)
      console.log("Fetching grocery suggestions for user:", user.userid)
      
      const response = await apiService.getGrocerySuggestions(user.userid)
      console.log("Grocery suggestions response:", response.data)
      
      if (response.data && response.data.suggestions) {
        setGroceryList(response.data.suggestions)
      } else {
        // Fallback to empty list if no suggestions
        setGroceryList([])
      }
    } catch (error) {
      console.error("Error generating grocery suggestions:", error)
      // Fallback to empty list on error
      setGroceryList([])
    } finally {
      setLoading(false)
    }
  }

  const updateQuantity = (id: number, change: number) => {
    setGroceryList((items) =>
      items.map((item) => (item.id === id ? { ...item, quantity: Math.max(0, item.quantity + change) } : item)),
    )
  }

  const toggleItemSelection = (id: number) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedItems(newSelected)
  }

  const selectAllSuggested = () => {
    const suggestedIds = groceryList.filter((item) => item.suggested).map((item) => item.id)
    setSelectedItems(new Set(suggestedIds))
  }

  const downloadList = () => {
    const selectedGroceries = groceryList.filter((item) => selectedItems.has(item.id))
    const listText = selectedGroceries.map((item) => `${item.quantity} ${item.unit} ${item.name}`).join("\n")

    const blob = new Blob([listText], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "grocery-list.txt"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-red-600 bg-red-100"
      case "medium":
        return "text-yellow-600 bg-yellow-100"
      case "low":
        return "text-green-600 bg-green-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  const getGroceryStoreLinks = (itemName: string) => {
    const encodedName = encodeURIComponent(itemName)
    return {
      blinkit: `https://blinkit.com/search?q=${encodedName}`,
      zepto: `https://www.zeptonow.com/search?q=${encodedName}`,
      flipkart: `https://www.flipkart.com/grocery/search?q=${encodedName}`,
      amazon: `https://www.amazon.in/s?k=${encodedName}&i=grocery`
    }
  }

  const groupedItems = groceryList.reduce(
    (acc, item) => {
      if (!acc[item.category]) {
        acc[item.category] = []
      }
      acc[item.category].push(item)
      return acc
    },
    {} as Record<string, GroceryItem[]>,
  )

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-20 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (groceryList.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <ShoppingCartIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No grocery suggestions available</h2>
          <p className="text-gray-600 mb-4">
            We need more consumption data to provide personalized grocery suggestions. 
            Start by consuming items from your inventory!
          </p>
          <button
            onClick={generateGrocerySuggestions}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Refresh Suggestions
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Grocery Suggestions</h1>
        <p className="text-gray-600">Smart recommendations based on your consumption patterns and inventory</p>
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-wrap gap-4">
          <button
            onClick={selectAllSuggested}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center"
          >
            <CheckIcon className="w-4 h-4 mr-2" />
            Select All Suggested
          </button>
          <button
            onClick={downloadList}
            disabled={selectedItems.size === 0}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center"
          >
            <DocumentArrowDownIcon className="w-4 h-4 mr-2" />
            Download List ({selectedItems.size})
          </button>
        </div>
      </div>

      {/* Grocery Items by Category */}
      <div className="space-y-6">
        {Object.entries(groupedItems).map(([category, items]) => (
          <div key={category} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
            <div className="bg-gray-50 dark:bg-gray-700 px-6 py-3 border-b dark:border-gray-600">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{category}</h2>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {items.map((item) => (
                <div
                  key={item.id}
                  className={`p-6 transition-colors relative ${selectedItems.has(item.id) ? "bg-blue-50 dark:bg-blue-900/20" : "hover:bg-gray-50 dark:hover:bg-gray-700/50"}`}
                  onClick={(e) => {
                    // Only toggle selection if clicking on the item itself, not on links
                    if ((e.target as HTMLElement).closest('a') === null) {
                      // Allow default behavior for non-link clicks
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => toggleItemSelection(item.id)}
                        className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                          selectedItems.has(item.id) ? "border-blue-500 bg-blue-500" : "border-gray-300"
                        }`}
                      >
                        {selectedItems.has(item.id) && <CheckIcon className="w-3 h-3 text-white" />}
                      </button>

                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium text-gray-900 dark:text-white">{item.name}</h3>
                          {item.suggested && (
                            <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-2 py-1 rounded-full">Suggested</span>
                          )}
                          <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(item.priority)}`}>
                            {item.priority} priority
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{item.reason}</p>
                        
                        {/* Grocery Store Links - Made more prominent and clickable */}
                        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-700 relative z-10">
                          <p className="text-sm text-gray-700 dark:text-gray-300 font-bold mb-3 flex items-center gap-2">
                            <span className="text-lg">🛒</span>
                            <span>Buy from online stores:</span>
                          </p>
                          <div className="flex flex-wrap gap-3">
                            {Object.entries(getGroceryStoreLinks(item.name)).map(([store, url]) => (
                              <a
                                key={store}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center justify-center gap-2 text-base px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white transition-all duration-200 shadow-lg hover:shadow-xl font-semibold cursor-pointer transform hover:scale-110 active:scale-95 no-underline relative z-20"
                                style={{ pointerEvents: 'auto' }}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  e.preventDefault()
                                  window.open(url, '_blank', 'noopener,noreferrer')
                                  console.log(`Opening ${store} for ${item.name}: ${url}`)
                                }}
                              >
                                <span className="font-bold">{store.charAt(0).toUpperCase() + store.slice(1)}</span>
                                <ArrowTopRightOnSquareIcon className="w-5 h-5" />
                              </a>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateQuantity(item.id, -1)}
                          className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                        >
                          <MinusIcon className="w-4 h-4" />
                        </button>
                        <span className="w-16 text-center">
                          {item.quantity} {item.unit}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, 1)}
                          className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                        >
                          <PlusIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      {selectedItems.size > 0 && (
        <div className="fixed bottom-6 right-6 bg-white rounded-lg shadow-lg border p-4 max-w-sm">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900">Shopping List</h3>
            <ShoppingCartIcon className="w-5 h-5 text-gray-600" />
          </div>
          <p className="text-sm text-gray-600 mb-3">{selectedItems.size} items selected</p>
          <button
            onClick={downloadList}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
          >
            Download List
          </button>
        </div>
      )}
    </div>
  )
}

