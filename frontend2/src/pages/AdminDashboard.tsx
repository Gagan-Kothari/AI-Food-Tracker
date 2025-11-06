"use client"

import { useEffect, useState } from "react"
import { useAdmin } from "../contexts/AdminContext"
import { apiService } from "../services/api"

interface UserRow {
  id: number
  name: string
  email: string
  points: number
}

export default function AdminDashboard() {
  const { admin, logout } = useAdmin()
  const [users, setUsers] = useState<UserRow[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [addForm, setAddForm] = useState({ userid: "", barcode: "", expiry_date: "" })
  const [busy, setBusy] = useState(false)
  const token = admin?.token || ""

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiService.adminListUsers(token)
        setUsers(res.data)
      } catch {
        // ignore
      } finally {
        setLoadingUsers(false)
      }
    }
    if (token) load()
  }, [token])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try {
      await apiService.adminAddInventory(token, Number(addForm.userid), addForm.barcode, addForm.expiry_date)
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
      await apiService.adminRetrainUser(token, id)
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
      await apiService.trainModels(token)
      alert("Training triggered for all users")
    } catch {
      alert("Failed to trigger training")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <button onClick={logout} className="text-red-600">Logout</button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Users</h2>
            <button onClick={handleTrainAll} disabled={busy} className="bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-60">Train All Models</button>
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


