export default function FocusTimer() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Focus Timer</h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Use the Pomodoro technique to boost your productivity.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
        <div className="text-center">
          <div className="text-6xl font-bold text-gray-900 dark:text-white mb-4">25:00</div>
          <div className="space-x-4">
            <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg">
              Start
            </button>
            <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-2 rounded-lg">
              Pause
            </button>
            <button className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg">
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
