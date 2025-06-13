export default function MoodTracker() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Mood Tracker</h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Track your daily mood and energy levels.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
            How are you feeling today?
          </h3>
          <div className="grid grid-cols-5 gap-4 mb-8">
            {['😢', '😕', '😐', '😊', '😄'].map((emoji, index) => (
              <button
                key={index}
                className="text-4xl p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                {emoji}
              </button>
            ))}
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
            Save Mood
          </button>
        </div>
      </div>
    </div>
  )
}
