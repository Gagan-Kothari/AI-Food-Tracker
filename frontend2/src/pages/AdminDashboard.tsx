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

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Users</h2>
            <div className="flex gap-2">
              <button onClick={handleTrainAll} disabled={busy} className="bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-60">Train All Models</button>
              <button onClick={handleSendAlerts} disabled={busy} className="bg-yellow-600 text-white px-4 py-2 rounded-md disabled:opacity-60">Send Expiry Alerts</button>
            </div>
          </div>
          {loadingUsers ? (
            <div>Loading users...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="py-2 pr-4">ID</th>
                    <th className="py-2 pr-4">Name</th>
                    <th className="py-2 pr-4">Email</th>
                    <th className="py-2 pr-4">Points</th>
                    <th className="py-2 pr-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className="border-b">
                      <td className="py-2 pr-4">{u.id}</td>
                      <td className="py-2 pr-4">{u.name}</td>
                      <td className="py-2 pr-4">{u.email}</td>
                      <td className="py-2 pr-4">{u.points}</td>
                      <td className="py-2 pr-4">
                        <button onClick={() => handleRetrain(u.id)} disabled={busy} className="text-green-700 hover:underline disabled:opacity-60">Retrain Model</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Add Food Item To Database</h2>
          <form onSubmit={handleAddFoodItem} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Barcode *</label>
                <input className="w-full border rounded px-3 py-2" placeholder="Barcode" value={foodItemForm.barcode} onChange={e => setFoodItemForm(s => ({ ...s, barcode: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Food Name *</label>
                <input className="w-full border rounded px-3 py-2" placeholder="Food Name" value={foodItemForm.f_name} onChange={e => setFoodItemForm(s => ({ ...s, f_name: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Brand *</label>
                <input className="w-full border rounded px-3 py-2" placeholder="Brand" value={foodItemForm.brands} onChange={e => setFoodItemForm(s => ({ ...s, brands: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                <input className="w-full border rounded px-3 py-2" placeholder="e.g., 100g, 250ml" value={foodItemForm.quantity} onChange={e => setFoodItemForm(s => ({ ...s, quantity: e.target.value }))} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Energy (kcal/100g) - Optional</label>
                <input type="number" className="w-full border rounded px-3 py-2" placeholder="Energy" value={foodItemForm.energy} onChange={e => setFoodItemForm(s => ({ ...s, energy: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                <select className="w-full border rounded px-3 py-2" value={foodItemForm.category} onChange={e => setFoodItemForm(s => ({ ...s, category: e.target.value }))} required>
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>
            <button type="submit" disabled={busy} className="bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-60">Add Food Item</button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Add Item To User Inventory</h2>
          <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input className="border rounded px-3 py-2" placeholder="User ID" value={addForm.userid} onChange={e => setAddForm(s => ({ ...s, userid: e.target.value }))} required />
            <input className="border rounded px-3 py-2" placeholder="Barcode" value={addForm.barcode} onChange={e => setAddForm(s => ({ ...s, barcode: e.target.value }))} required />
            <input className="border rounded px-3 py-2" placeholder="Expiry Date (YYYY-MM-DD)" value={addForm.expiry_date} onChange={e => setAddForm(s => ({ ...s, expiry_date: e.target.value }))} required />
            <button type="submit" disabled={busy} className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-60">Add Item</button>
          </form>
        </div>
      </div>
    </div>
  )
}


