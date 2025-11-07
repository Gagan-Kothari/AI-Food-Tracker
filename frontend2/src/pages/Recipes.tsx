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
  const [inventoryCount, setInventoryCount] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [recipeType, setRecipeType] = useState<"indian" | "foreign" | "both">("foreign")

  useEffect(() => {
    fetchInventoryAndRecipes()
  }, [user, recipeType])

  const fetchInventoryAndRecipes = async () => {
    if (!user?.userid) return

    try {
      setLoading(true)
      setError(null)

      // Get inventory-based recipe suggestions
      console.log("Fetching inventory-based recipes for user:", user.userid, "type:", recipeType)
      const recipeResponse = await apiService.getInventoryBasedRecipes(user.userid, recipeType)
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
            unit: ing.unit || "item",
            category: ing.category,
            daysUntilExpiry: ing.days_until_expiry,
            available: ing.available !== false  // Default to true if not specified
          })) || [],
          missedIngredients: recipe.missedIngredients?.map((ing: any) => ({
            id: ing.id,
            name: ing.name,
            image: ing.image || "/placeholder.svg",
            available: false
          })) || []
        }))

        // Sort by priority score (highest first)
        transformedRecipes.sort((a, b) => (b.priorityScore || 0) - (a.priorityScore || 0))

        setRecipes(transformedRecipes)
        
        // Update inventory count from summary
        if (recipeResponse.data.inventory_summary) {
          const summary = recipeResponse.data.inventory_summary
          setInventoryCount(summary.total_items || 0)
          console.log(`Found ${summary.total_items} items in inventory, ${summary.expiring_soon} expiring soon`)
        } else if (recipeResponse.data.ingredients_used) {
          // Fallback: use ingredients_used count
          setInventoryCount(recipeResponse.data.ingredients_used.length || 0)
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

  const handleCookedRecipe = async () => {
    if (!selectedRecipe || !user?.userid) return
    
    try {
      const response = await apiService.markRecipeAsCooked(
        user.userid,
        selectedRecipe.id,
        selectedRecipe.title,
        selectedRecipe.usedIngredients
      )
      
      if (response.data.status) {
        alert("Great! Recipe marked as cooked. Check your WhatsApp for a special message! 🎉")
        setSelectedRecipe(null)
        // Refresh recipes to update the list
        fetchInventoryAndRecipes()
      } else {
        alert("Failed to mark recipe as cooked. Please try again.")
      }
    } catch (error) {
      console.error("Error marking recipe as cooked:", error)
      alert("Failed to mark recipe as cooked. Please try again.")
    }
  }

  const retryFetch = () => {
    fetchInventoryAndRecipes()
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 dark:bg-gray-700 h-80 rounded-lg"></div>
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
          <BookOpenIcon className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Unable to load recipes</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <button
            onClick={retryFetch}
            className="bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Recipe Suggestions</h1>
        <p className="text-gray-600 dark:text-gray-400">
          AI-powered recipes based on your current inventory ({inventoryCount} items)
        </p>
      </div>

      {/* Recipe Type Buttons */}
      <div className="mb-6 flex flex-wrap gap-3 justify-center sm:justify-start">
        <button
          onClick={() => setRecipeType("indian")}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            recipeType === "indian"
              ? "bg-green-600 dark:bg-green-500 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
          }`}
        >
          Indian Recipes
        </button>
        <button
          onClick={() => setRecipeType("foreign")}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            recipeType === "foreign"
              ? "bg-green-600 dark:bg-green-500 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
          }`}
        >
          Foreign Recipes
        </button>
        <button
          onClick={() => setRecipeType("both")}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            recipeType === "both"
              ? "bg-green-600 dark:bg-green-500 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
          }`}
        >
          Both
        </button>
      </div>

      {recipes.length === 0 ? (
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No recipes found</h2>
          <p className="text-gray-600 dark:text-gray-400">Try adding more ingredients to your inventory for better recipe suggestions</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes.map((recipe) => (
            <div
              key={recipe.id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow overflow-hidden border border-gray-200 dark:border-gray-700 flex flex-col h-full"
            >
              <img src={recipe.image || "/placeholder.svg"} alt={recipe.title} className="w-full h-48 object-cover flex-shrink-0" />
              <div className="p-6 flex flex-col flex-1">
                <div className="flex items-start justify-between mb-2 min-h-[3rem]">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1 pr-2">{recipe.title}</h3>
                  {recipe.priorityScore && recipe.priorityScore > 0 ? (
                    <span className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${
                      recipe.priorityScore >= 10 
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' 
                        : recipe.priorityScore >= 5 
                          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
                          : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                    }`}>
                      {recipe.priorityScore >= 10 ? 'High Priority' : recipe.priorityScore >= 5 ? 'Medium Priority' : 'Low Priority'}
                    </span>
                  ) : (
                    <span className="w-0 h-0"></span>
                  )}
                </div>

                <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600 dark:text-gray-400">
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
                  <div className="flex items-center justify-between mb-2 min-h-[1.5rem]">
                    <span className="text-sm font-medium text-green-600 dark:text-green-400">
                      You have: {recipe.usedIngredientCount} ingredients
                    </span>
                    {recipe.missedIngredientCount > 0 ? (
                      <span className="text-sm text-orange-600 dark:text-orange-400">Need: {recipe.missedIngredientCount} more</span>
                    ) : (
                      <span className="text-sm text-transparent">Need: 0 more</span>
                    )}
                  </div>

                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 dark:bg-green-400 h-2 rounded-full"
                      style={{
                        width: `${(recipe.usedIngredientCount / (recipe.usedIngredientCount + recipe.missedIngredientCount)) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-3 flex-1 mb-4">
                  {recipe.usedIngredients.length > 0 ? (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">Ingredients you have:</h4>
                      <div className="flex flex-wrap gap-1">
                        {recipe.usedIngredients.map((ingredient) => {
                          const isExpiringSoon = ingredient.daysUntilExpiry !== undefined && ingredient.daysUntilExpiry <= 3
                          const isExpiringThisWeek = ingredient.daysUntilExpiry !== undefined && ingredient.daysUntilExpiry <= 7
                          
                          return (
                            <span
                              key={ingredient.id}
                              className={`inline-block text-xs px-2 py-1 rounded-full ${
                                isExpiringSoon 
                                  ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800' 
                                  : isExpiringThisWeek 
                                    ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800'
                                    : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
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
                  ) : (
                    <div className="min-h-[2.5rem]"></div>
                  )}

                  {recipe.missedIngredients.length > 0 ? (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">Missing ingredients:</h4>
                      <div className="flex flex-wrap gap-1">
                        {recipe.missedIngredients.map((ingredient) => (
                          <span
                            key={ingredient.id}
                            className="inline-block bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 text-xs px-2 py-1 rounded-full"
                          >
                            {ingredient.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="min-h-[2.5rem]"></div>
                  )}
                </div>

                <div className="mt-auto space-y-2 pt-4">
                  <button
                    onClick={() => setSelectedRecipe(recipe)}
                    className="w-full bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                  >
                    View Recipe
                  </button>
                  <button
                    onClick={() => handleCookedRecipe()}
                    className="w-full bg-green-600 dark:bg-green-500 hover:bg-green-700 dark:hover:bg-green-600 text-white py-2 px-4 rounded-lg font-medium transition-colors"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedRecipe.title}</h2>
                <button onClick={() => setSelectedRecipe(null)} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
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
                  <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">Ingredients</h3>
                  <div className="space-y-2">
                    {[...selectedRecipe.usedIngredients, ...selectedRecipe.missedIngredients].map((ingredient) => (
                      <div key={ingredient.id} className="flex items-center space-x-2">
                        <span
                          className={`w-3 h-3 rounded-full ${
                            selectedRecipe.usedIngredients.find((i) => i.id === ingredient.id)
                              ? "bg-green-500 dark:bg-green-400"
                              : "bg-orange-500 dark:bg-orange-400"
                          }`}
                        ></span>
                        <span className="text-gray-700 dark:text-gray-300">{ingredient.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">Instructions</h3>
                  <ol className="list-decimal list-inside space-y-2 text-gray-700 dark:text-gray-300">
                    <li>Prepare all ingredients and wash vegetables thoroughly.</li>
                    <li>Heat oil in a large pan or wok over medium-high heat.</li>
                    <li>Add aromatics (garlic, onions) and cook until fragrant.</li>
                    <li>Add main ingredients and cook according to recipe requirements.</li>
                    <li>Season to taste and serve immediately while hot.</li>
                  </ol>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => handleCookedRecipe()}
                  className="w-full bg-green-600 dark:bg-green-500 hover:bg-green-700 dark:hover:bg-green-600 text-white py-3 px-4 rounded-lg font-medium transition-colors"
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
