"use client"

export default function PrivacyPolicy() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Privacy Policy</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Last updated: {new Date().toLocaleDateString()}</p>
      </div>

      <div className="space-y-8">
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">1. Information We Collect</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            We collect information that you provide directly to us, including:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>Account information (name, email, phone number)</li>
            <li>Food inventory data (items, expiry dates, quantities)</li>
            <li>Location data (when you use features like NGO search)</li>
            <li>Usage data (how you interact with our services)</li>
          </ul>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">2. How We Use Your Information</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            We use the information we collect to:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>Provide and improve our services</li>
            <li>Send you notifications about expiring items</li>
            <li>Generate personalized recipe and grocery recommendations</li>
            <li>Process donations and manage your points</li>
            <li>Send WhatsApp notifications (with your consent)</li>
          </ul>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">3. Data Storage and Security</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            We take the security of your data seriously. Your information is stored securely using industry-standard 
            encryption and security measures. We do not sell or share your personal information with third parties 
            except as necessary to provide our services (e.g., WhatsApp API for notifications).
          </p>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">4. Location Data</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            We only access your location when you explicitly request features that require it (such as finding nearby NGOs). 
            Location data is used solely for the purpose you requested and is not stored permanently or shared with third parties.
          </p>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">5. Your Rights</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            You have the right to:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>Access your personal data</li>
            <li>Correct inaccurate information</li>
            <li>Delete your account and data</li>
            <li>Opt-out of notifications</li>
            <li>Request a copy of your data</li>
          </ul>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">6. Contact Us</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            If you have any questions about this Privacy Policy or wish to exercise your rights, please contact us 
            through our <a href="/contact" className="text-blue-600 dark:text-blue-400 hover:underline">Contact page</a>.
          </p>
        </section>
      </div>
    </div>
  )
}

