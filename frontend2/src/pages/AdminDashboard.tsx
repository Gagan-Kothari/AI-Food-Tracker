"use client"

import { useEffect, useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useNavigate } from "react-router-dom"
import { useDarkMode } from "../contexts/DarkModeContext"
import { apiService } from "../services/api"
import { SunIcon, MoonIcon } from "@heroicons/react/24/outline"

interface UserRow {
  id: number
  name: string
  email: string
  points: number
}

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const { darkMode, toggleDarkMode } = useDarkMode()
  const navigate = useNavigate()
  const [users, setUsers] = useState<UserRow[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [addForm, setAddForm] = useState({ userid: "", barcode: "", expiry_date: "" })
  const [foodItemForm, setFoodItemForm] = useState({ barcode: "", f_name: "", brands: "", quantity: "", energy: "", category: "" })
  const [categories, setCategories] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const adminUserid = user ? Number(user.userid) : 0

  useEffect(() => {
    if (!user || !user.isAdmin) {
      navigate("/login")
      return
    }
    const load = async () => {
      try {
        const res = await apiService.adminListUsers(adminUserid)
        setUsers(res.data)
      } catch {
        // ignore
      } finally {
        setLoadingUsers(false)
      }
    }
    const loadCategories = async () => {
      try {
        const res = await apiService.getCategories()
        setCategories(res.data.categories || [])
      } catch {
        // ignore
      }
    }
    if (adminUserid > 0) {
      load()
      loadCategories()
    }
  }, [adminUserid, user, navigate])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try {
      await apiService.adminAddInventory(adminUserid, Number(addForm.userid), addForm.barcode, addForm.expiry_date)
      alert("Item added to inventory")
      setAddForm({ userid: "", barcode: "", expiry_date: "" })
    } catch {
      alert("Failed to add item")
    } finally {
      setBusy(false)
    }
  }

  const handleRetrain = async (id: number) => {
    setBusy(true)
    try {
      await apiService.adminRetrainUser(adminUserid, id)
      alert("Retraining triggered")
    } catch {
      alert("Failed to retrain user model")
    } finally {
      setBusy(false)
    }
  }

  const handleTrainAll = async () => {
    setBusy(true)
    try {
      await apiService.adminTrainAll(adminUserid)
      alert("Training triggered for all users")
    } catch {
      alert("Failed to trigger training")
    } finally {
      setBusy(false)
    }
  }

  const handleSendAlerts = async () => {
    setBusy(true)
    try {
      const response = await apiService.adminSendExpiryAlerts(adminUserid)
      if (response.data.status) {
        const alerts = response.data.alerts_sent
        alert(`Alerts sent successfully!\nYellow: ${alerts.yellow}\nRed: ${alerts.red}\nGrey: ${alerts.grey}`)
      } else {
        alert(response.data.message || "Failed to send alerts")
      }
    } catch {
      alert("Failed to send expiry alerts")
    } finally {
      setBusy(false)
    }
  }

  const handleAddFoodItem = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try {
      const response = await apiService.adminAddFoodItem(
        adminUserid,
        foodItemForm.barcode,
        foodItemForm.f_name,
        foodItemForm.brands,
        foodItemForm.quantity,
        foodItemForm.energy ? parseInt(foodItemForm.energy) : null,
        foodItemForm.category
      )
      if (response.data.status) {
        alert("Food item added to database successfully!")
        setFoodItemForm({ barcode: "", f_name: "", brands: "", quantity: "", energy: "", category: "" })
      } else {
        alert(response.data.message || "Failed to add food item")
      }
    } catch {
      alert("Failed to add food item")
    } finally {
      setBusy(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 transition-colors">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <div className="flex items-center gap-4">
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
            <button onClick={handleLogout} className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium">Logout</button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Users</h2>
            <div className="flex gap-2">
              <button onClick={handleTrainAll} disabled={busy} className="bg-green-600 dark:bg-green-500 hover:bg-green-700 dark:hover:bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-60 transition-colors">Train All Models</button>
              <button onClick={handleSendAlerts} disabled={busy} className="bg-yellow-600 dark:bg-yellow-500 hover:bg-yellow-700 dark:hover:bg-yellow-600 text-white px-4 py-2 rounded-md disabled:opacity-60 transition-colors">Send Expiry Alerts</button>
            </div>
          </div>
          {loadingUsers ? (
            <div className="text-gray-600 dark:text-gray-400">Loading users...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left border-b border-gray-200 dark:border-gray-700">
                    <th className="py-2 pr-4 text-gray-900 dark:text-white">ID</th>
                    <th className="py-2 pr-4 text-gray-900 dark:text-white">Name</th>
                    <th className="py-2 pr-4 text-gray-900 dark:text-white">Email</th>
                    <th className="py-2 pr-4 text-gray-900 dark:text-white">Points</th>
                    <th className="py-2 pr-4 text-gray-900 dark:text-white">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-2 pr-4 text-gray-700 dark:text-gray-300">{u.id}</td>
                      <td className="py-2 pr-4 text-gray-700 dark:text-gray-300">{u.name}</td>
                      <td className="py-2 pr-4 text-gray-700 dark:text-gray-300">{u.email}</td>
                      <td className="py-2 pr-4 text-gray-700 dark:text-gray-300">{u.points}</td>
                      <td className="py-2 pr-4">
                        <button onClick={() => handleRetrain(u.id)} disabled={busy} className="text-green-700 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300 hover:underline disabled:opacity-60 transition-colors">Retrain Model</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 transition-colors">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Add Food Item To Database</h2>
          <form onSubmit={handleAddFoodItem} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Barcode *</label>
                <input className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="Barcode" value={foodItemForm.barcode} onChange={e => setFoodItemForm(s => ({ ...s, barcode: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Food Name *</label>
                <input className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="Food Name" value={foodItemForm.f_name} onChange={e => setFoodItemForm(s => ({ ...s, f_name: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Brand *</label>
                <input className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="Brand" value={foodItemForm.brands} onChange={e => setFoodItemForm(s => ({ ...s, brands: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Quantity *</label>
                <input className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="e.g., 100g, 250ml" value={foodItemForm.quantity} onChange={e => setFoodItemForm(s => ({ ...s, quantity: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Energy (kcal/100g) - Optional</label>
                <input type="number" className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="Energy" value={foodItemForm.energy} onChange={e => setFoodItemForm(s => ({ ...s, energy: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category *</label>
                <select className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent" value={foodItemForm.category} onChange={e => setFoodItemForm(s => ({ ...s, category: e.target.value }))} required>
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>
            <button type="submit" disabled={busy} className="bg-green-600 dark:bg-green-500 hover:bg-green-700 dark:hover:bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-60 transition-colors">Add Food Item</button>
          </form>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 transition-colors">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Add Item To User Inventory</h2>
          <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input className="border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="User ID" value={addForm.userid} onChange={e => setAddForm(s => ({ ...s, userid: e.target.value }))} required />
            <input className="border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Barcode" value={addForm.barcode} onChange={e => setAddForm(s => ({ ...s, barcode: e.target.value }))} required />
            <input className="border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Expiry Date (YYYY-MM-DD)" value={addForm.expiry_date} onChange={e => setAddForm(s => ({ ...s, expiry_date: e.target.value }))} required />
            <button type="submit" disabled={busy} className="bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-60 transition-colors">Add Item</button>
          </form>
        </div>
      </div>
    </div>
  )
}


