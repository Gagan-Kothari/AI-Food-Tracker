import axios from "axios"

function normalizeBaseUrl(value: string | undefined): string {
  if (!value || value.trim() === "") return "/api"
  const v = value.trim()
  if (v.startsWith("http://") || v.startsWith("https://") || v.startsWith("/")) return v
  return `https://${v}`
}

const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL)

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// API functions
export const apiService = {
  // Auth
  login: (email: string, password: string) => api.post("/user/verify", { email, password }),

  signup: (name: string, email: string, password: string) => api.post("/user/add", { name, email, password }),

  // Inventory
  getInventory: (userid: string) => api.post("/user/inventory", {userid}),
  
  // Mark item as consumed/donated/expired
  updateFoodStatus: (inventory_id: number, status: string, notes: string) => 
    api.post("/user/foodstatus", { inventory_id, status, notes }),
  
  // Delete inventory item
  deleteInventoryItem: (inventory_id: number, userid: string) => 
    api.delete(`/user/inventory/${inventory_id}?userid=${userid}`),
  
  // Mark items as donated
  donateItems: (inventory_ids: number[], userid: string) => 
    api.post("/user/donate", { inventory_ids, userid }),
  
  // Get user points
  getUserPoints: (userid: string) => api.get(`/user/points/${userid}`),



  // Scan item
  scanItem: (barcode: string, expiry_date: string, userid: string) => api.post("/item/scan", { barcode, expiry_date, userid }),

  // Recipe suggestions
  getRecipeSuggestions: (ingredients: string[]) => api.post("/user/recipe/suggestions", { ingredients }),
  getInventoryBasedRecipes: (userid: string) => api.post("/user/recipe/inventory-based", { userid }),

  // Grocery suggestions
  getGrocerySuggestions: (userid: string) => api.post("/user/grocery-suggestions", { userid }),

  // Model training
  trainModels: (adminToken?: string) => api.post("/admin/train-models", {}, { headers: { "x-admin-token": adminToken || "" } }),
  retrainUserModel: (userid: string) => api.post("/user/retrain-model", { userid }),

  // Verify item by barcode
  verifyItem: (barcode: string) => api.post("/admin/verifyitem", { barcode }),

  // Admin
  adminListUsers: (adminUserid: number) => api.post("/admin/users", { userid: adminUserid }),
  adminAddInventory: (adminUserid: number, targetUserid: number, barcode: string, expiry_date: string) =>
    api.post("/admin/inventory/add", { admin_userid: adminUserid, userid: targetUserid, barcode, expiry_date }),
  adminRetrainUser: (adminUserid: number, targetUserid: number) =>
    api.post("/admin/user/retrain", { admin_userid: adminUserid, target_userid: targetUserid }),
  adminTrainAll: (adminUserid: number) => api.post("/admin/train-models", { userid: adminUserid }),
  adminAddFoodItem: (adminUserid: number, barcode: string, f_name: string, brands: string, quantity: string, energy: number | null, category: string) =>
    api.post("/admin/food-item/add", { admin_userid: adminUserid, barcode, f_name, brands, quantity, energy, category }),

  // Manual item entry
  manualAddItem: (barcode: string, f_name: string, brands: string, quantity: string, energy: number | null, category: string, expiry_date: string, userid: string) =>
    api.post("/item/manual-add", { barcode, f_name, brands, quantity, energy, category, expiry_date, userid }),

  // Get categories
  getCategories: () => api.get("/categories"),
}
