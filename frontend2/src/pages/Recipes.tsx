"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { apiService } from "../services/api"
import { BookOpenIcon, ClockIcon, UsersIcon } from "@heroicons/react/24/outline"

interface Recipe {
  id: number
  title: string
  image: string
  usedIngredientCount: number
  missedIngredientCount: number
  priorityScore?: number
  usedIngredients: Array<{
    id: number
    name: string
    image: string
    inventoryId?: number
    expiryDate?: string
    quantity?: number
    unit?: string
    category?: string
    daysUntilExpiry?: number
  }>
  missedIngredients: Array<{
    id: number
    name: string
    image: string
  }>
}

export default function Recipes() {
  const { user } = useAuth()
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [inventory, setInventory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)

  useEffect(() => {
    fetchInventoryAndRecipes()
  }, [user])

  const fetchInventoryAndRecipes = async () => {
    if (!user?.userid) return

    try {
      setLoading(true)
      setError(null)

      // Get inventory-based recipe suggestions
      console.log("Fetching inventory-based recipes for user:", user.userid)
      const recipeResponse = await apiService.getInventoryBasedRecipes(user.userid)
      console.log("Inventory-based recipe API response:", recipeResponse.data)
      
      if (recipeResponse.data.success && recipeResponse.data.recipes) {
        // Transform API response to match our interface
        const transformedRecipes: Recipe[] = recipeResponse.data.recipes.map((recipe: any) => ({
          id: recipe.id,
          title: recipe.title,
          image: recipe.image || "/placeholder.svg",
          usedIngredientCount: recipe.usedIngredientCount || 0,
          missedIngredientCount: recipe.missedIngredientCount || 0,
          priorityScore: recipe.priority_score || 0,
          usedIngredients: recipe.usedIngredients?.map((ing: any) => ({
            id: ing.id,
            name: ing.name,
            image: ing.image || "/placeholder.svg",
            inventoryId: ing.inventory_id,
            expiryDate: ing.expiry_date,
            quantity: ing.quantity,
            unit: ing.unit,
            category: ing.category,
            daysUntilExpiry: ing.days_until_expiry
          })) || [],
          missedIngredients: recipe.missedIngredients?.map((ing: any) => ({
            id: ing.id,
            name: ing.name,
            image: ing.image || "/placeholder.svg"
          })) || []
        }))

        // Sort by priority score (highest first)
        transformedRecipes.sort((a, b) => (b.priorityScore || 0) - (a.priorityScore || 0))

        setRecipes(transformedRecipes)
        
        // Show inventory summary if available
        if (recipeResponse.data.inventory_summary) {
          const summary = recipeResponse.data.inventory_summary
          console.log(`Found ${summary.total_items} items in inventory, ${summary.expiring_soon} expiring soon`)
        }
      } else {
        setError(recipeResponse.data.error || "No ingredients found in inventory")
      }
    } catch (error) {
      console.error("Error fetching recipes:", error)
      setError("Failed to load recipe suggestions")
    } finally {
      setLoading(false)
    }
  }

  const handleCookedRecipe = (recipeId: number) => {
    // In a real app, this would log the recipe as cooked
    alert("Great! Recipe marked as cooked. This helps us improve our suggestions.")
  }

  const retryFetch = () => {
    fetchInventoryAndRecipes()
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-80 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to load recipes</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={retryFetch}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recipe Suggestions</h1>
        <p className="text-gray-600">
          AI-powered recipes based on your current inventory ({inventory.length} items)
        </p>
      </div>

      {inventory.length === 0 ? (
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No inventory items found</h2>
          <p className="text-gray-600">Add items to your inventory to get personalized recipe suggestions</p>
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No recipes found</h2>
          <p className="text-gray-600">Try adding more ingredients to your inventory for better recipe suggestions</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes.map((recipe) => (
            <div
              key={recipe.id}
              className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow overflow-hidden"
            >
              <img src={recipe.image || "/placeholder.svg"} alt={recipe.title} className="w-full h-48 object-cover" />
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{recipe.title}</h3>
                  {recipe.priorityScore && recipe.priorityScore > 0 && (
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      recipe.priorityScore >= 10 
                        ? 'bg-red-100 text-red-800' 
                        : recipe.priorityScore >= 5 
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                    }`}>
                      {recipe.priorityScore >= 10 ? 'High Priority' : recipe.priorityScore >= 5 ? 'Medium Priority' : 'Low Priority'}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    <span>30 min</span>
                  </div>
                  <div className="flex items-center">
                    <UsersIcon className="h-4 w-4 mr-1" />
                    <span>2-4 servings</span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-green-600">
                      You have: {recipe.usedIngredientCount} ingredients
                    </span>
                    {recipe.missedIngredientCount > 0 && (
                      <span className="text-sm text-orange-600">Need: {recipe.missedIngredientCount} more</span>
                    )}
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{
                        width: `${(recipe.usedIngredientCount / (recipe.usedIngredientCount + recipe.missedIngredientCount)) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-3">
                  {recipe.usedIngredients.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-1">Ingredients you have:</h4>
                      <div className="flex flex-wrap gap-1">
                        {recipe.usedIngredients.map((ingredient) => {
                          const isExpiringSoon = ingredient.daysUntilExpiry !== undefined && ingredient.daysUntilExpiry <= 3
                          const isExpiringThisWeek = ingredient.daysUntilExpiry !== undefined && ingredient.daysUntilExpiry <= 7
                          
                          return (
                            <span
                              key={ingredient.id}
                              className={`inline-block text-xs px-2 py-1 rounded-full ${
                                isExpiringSoon 
                                  ? 'bg-red-100 text-red-800 border border-red-200' 
                                  : isExpiringThisWeek 
                                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                                    : 'bg-green-100 text-green-800'
                              }`}
                              title={
                                ingredient.daysUntilExpiry !== undefined 
                                  ? `Expires in ${ingredient.daysUntilExpiry} days${ingredient.quantity ? ` (${ingredient.quantity} ${ingredient.unit})` : ''}`
                                  : ingredient.quantity 
                                    ? `${ingredient.quantity} ${ingredient.unit}`
                                    : ''
                              }
                            >
                              {ingredient.name}
                              {isExpiringSoon && ' ⚠️'}
                            </span>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {recipe.missedIngredients.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-1">Missing ingredients:</h4>
                      <div className="flex flex-wrap gap-1">
                        {recipe.missedIngredients.map((ingredient) => (
                          <span
                            key={ingredient.id}
                            className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full"
                          >
                            {ingredient.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 space-y-2">
                  <button
                    onClick={() => setSelectedRecipe(recipe)}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                  >
                    View Recipe
                  </button>
                  <button
                    onClick={() => handleCookedRecipe(recipe.id)}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                  >
                    I Cooked This!
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Recipe Detail Modal */}
      {selectedRecipe && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedRecipe.title}</h2>
                <button onClick={() => setSelectedRecipe(null)} className="text-gray-500 hover:text-gray-700">
                  ✕
                </button>
              </div>

              <img
                src={selectedRecipe.image || "/placeholder.svg"}
                alt={selectedRecipe.title}
                className="w-full h-64 object-cover rounded-lg mb-6"
              />

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-3">Ingredients</h3>
                  <div className="space-y-2">
                    {[...selectedRecipe.usedIngredients, ...selectedRecipe.missedIngredients].map((ingredient) => (
                      <div key={ingredient.id} className="flex items-center space-x-2">
                        <span
                          className={`w-3 h-3 rounded-full ${
                            selectedRecipe.usedIngredients.find((i) => i.id === ingredient.id)
                              ? "bg-green-500"
                              : "bg-orange-500"
                          }`}
                        ></span>
                        <span>{ingredient.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Instructions</h3>
                  <ol className="list-decimal list-inside space-y-2 text-gray-700">
                    <li>Prepare all ingredients and wash vegetables thoroughly.</li>
                    <li>Heat oil in a large pan or wok over medium-high heat.</li>
                    <li>Add aromatics (garlic, onions) and cook until fragrant.</li>
                    <li>Add main ingredients and cook according to recipe requirements.</li>
                    <li>Season to taste and serve immediately while hot.</li>
                  </ol>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t">
                <button
                  onClick={() => handleCookedRecipe(selectedRecipe.id)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  Mark as Cooked
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
