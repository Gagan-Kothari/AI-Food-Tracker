"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { apiService } from "../services/api"
import { CameraIcon } from "@heroicons/react/24/outline"
import BarcodeScanner from "../components/BarcodeScanner"

export default function Scan() {
  const { user } = useAuth()
  const [expiryDate, setExpiryDate] = useState("")
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [showScanner, setShowScanner] = useState(false)
  const [showManualForm, setShowManualForm] = useState(false)
  const [scannedBarcode, setScannedBarcode] = useState("")
  const [categories, setCategories] = useState<string[]>([])
  const [manualForm, setManualForm] = useState({
    f_name: "",
    brands: "",
    quantity: "",
    energy: "",
    category: "",
  })

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await apiService.getCategories()
        setCategories(res.data.categories || [])
      } catch (error) {
        console.error("Error loading categories:", error)
      }
    }
    loadCategories()
  }, [])

  const handleBarcodeDetected = async (barcode: string) => {
    setShowScanner(false)
    
    if (!user?.userid || !expiryDate) {
      setMessage("Please select an expiry date first")
      return
    }

    setLoading(true)
    setMessage("Processing barcode...")
    
    try {
      const response = await apiService.scanItem(barcode, expiryDate, user.userid)
      
      if (response.data.status || response.data.message === "success") {
        setMessage(`Item added to inventory successfully! (Source: ${response.data.source || "unknown"})`)
        setExpiryDate("")
        setShowManualForm(false)
        setScannedBarcode("")
      } else if (response.data.requires_manual) {
        // Item not found, ask user if they want to add manually
        setScannedBarcode(barcode)
        setShowManualForm(true)
        setMessage("Item not found. Please fill in the details below to add it manually.")
      } else {
        setMessage(response.data.message || "Failed to add item to inventory")
      }
    } catch (error) {
      console.error("Scan error:", error)
      setMessage("Error processing barcode. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user?.userid || !expiryDate) {
      setMessage("Please select an expiry date first")
      return
    }

    setLoading(true)
    try {
      const response = await apiService.manualAddItem(
        scannedBarcode,
        manualForm.f_name,
        manualForm.brands,
        manualForm.quantity,
        manualForm.energy ? parseInt(manualForm.energy) : null,
        manualForm.category,
        expiryDate,
        user.userid
      )

      if (response.data.status) {
        setMessage("Item added to inventory successfully!")
        setExpiryDate("")
        setShowManualForm(false)
        setScannedBarcode("")
        setManualForm({ f_name: "", brands: "", quantity: "", energy: "", category: "" })
      } else {
        setMessage(response.data.message || "Failed to add item")
      }
    } catch (error) {
      console.error("Manual add error:", error)
      setMessage("Error adding item. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const startScanning = () => {
    if (!expiryDate) {
      setMessage("Please select an expiry date first")
      return
    }
    setShowScanner(true)
    setMessage("")
    setShowManualForm(false)
  }

  const resetForm = () => {
    setExpiryDate("")
    setMessage("")
    setShowManualForm(false)
    setScannedBarcode("")
    setManualForm({ f_name: "", brands: "", quantity: "", energy: "", category: "" })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Scan Item</h1>
        <p className="text-gray-600">Scan barcodes to add items to your inventory</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        {!showManualForm ? (
          <div className="text-center">
            <div className="mb-6">
              <CameraIcon className="mx-auto h-24 w-24 text-gray-400" />
            </div>
            
            <div className="mb-6">
              <label htmlFor="expiryDate" className="block text-sm font-medium text-gray-700 mb-2">
                Expiry Date *
              </label>
              <input
                type="date"
                id="expiryDate"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
                className="w-full max-w-md mx-auto px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              onClick={startScanning}
              disabled={loading || !expiryDate}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-lg font-medium transition-colors"
            >
              {loading ? "Processing..." : "Scan Barcode & Add to Inventory"}
            </button>

            {message && (
              <div
                className={`mt-4 p-4 rounded-lg ${
                  message.includes("success") ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                }`}
              >
                {message}
              </div>
            )}

            {!loading && message.includes("success") && (
              <button
                onClick={resetForm}
                className="mt-4 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Scan Another Item
              </button>
            )}
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-semibold mb-4">Manual Entry</h2>
            <p className="text-sm text-gray-600 mb-4">Barcode: {scannedBarcode}</p>
            <form onSubmit={handleManualSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Food Name *</label>
                <input
                  type="text"
                  value={manualForm.f_name}
                  onChange={(e) => setManualForm({ ...manualForm, f_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Brand *</label>
                <input
                  type="text"
                  value={manualForm.brands}
                  onChange={(e) => setManualForm({ ...manualForm, brands: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                <input
                  type="text"
                  value={manualForm.quantity}
                  onChange={(e) => setManualForm({ ...manualForm, quantity: e.target.value })}
                  placeholder="e.g., 100g, 250ml"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Energy (kcal/100g) - Optional</label>
                <input
                  type="number"
                  value={manualForm.energy}
                  onChange={(e) => setManualForm({ ...manualForm, energy: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                <select
                  value={manualForm.category}
                  onChange={(e) => setManualForm({ ...manualForm, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  {loading ? "Adding..." : "Add Item"}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
            {message && (
              <div
                className={`mt-4 p-4 rounded-lg ${
                  message.includes("success") ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                }`}
              >
                {message}
              </div>
            )}
          </div>
        )}
      </div>

      {showScanner && (
        <BarcodeScanner
          onBarcodeDetected={handleBarcodeDetected}
          onClose={() => setShowScanner(false)}
        />
      )}
    </div>
  )
}
