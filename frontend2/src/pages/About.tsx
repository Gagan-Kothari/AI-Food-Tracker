"use client"

export default function About() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">About FoodTracker</h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">Smart food management to reduce waste and save money</p>
      </div>

      <div className="space-y-8">
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Our Mission</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            FoodTracker is dedicated to helping individuals and families reduce food waste while saving money. 
            We believe that smart food management can make a significant impact on both personal finances and 
            environmental sustainability.
          </p>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Key Features</h2>
          <ul className="space-y-3 text-gray-700 dark:text-gray-300">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Smart Inventory Management:</strong> Track your food items with expiry dates and get alerts before they expire</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Recipe Suggestions:</strong> Get personalized recipe recommendations based on items in your inventory</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Donation Platform:</strong> Easily donate items to nearby NGOs and earn points</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>AI-Powered Grocery Recommendations:</strong> Get smart suggestions for your next grocery shopping</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Rewards Marketplace:</strong> Redeem points for exclusive coupons and discounts</span>
            </li>
          </ul>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">How It Works</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 dark:bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                1
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Scan & Add</h3>
                <p className="text-gray-700 dark:text-gray-300">Scan barcodes or manually add food items to your inventory</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 dark:bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                2
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Get Alerts</h3>
                <p className="text-gray-700 dark:text-gray-300">Receive notifications when items are about to expire</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 dark:bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                3
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Cook or Donate</h3>
                <p className="text-gray-700 dark:text-gray-300">Use recipes to cook with expiring items or donate to NGOs</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 dark:bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                4
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Earn & Redeem</h3>
                <p className="text-gray-700 dark:text-gray-300">Earn points for donations and redeem them for exclusive coupons</p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Impact</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            By using FoodTracker, you're contributing to a more sustainable future. Every item saved from 
            expiring or donated to those in need makes a difference. Together, we can reduce food waste 
            and help feed communities.
          </p>
        </section>
      </div>
    </div>
  )
}

