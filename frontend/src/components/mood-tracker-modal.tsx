'use client'

import { useState } from 'react'
import { X, Smile, Meh, Frown, HeartCrack, PartyPopper } from 'lucide-react'
import { api, OfflineStorage, useNetworkStatus, type MoodData } from '@/lib/api'

interface MoodTrackerModalProps {
  isOpen: boolean
  onClose: () => void
  sessionType: 'focus' | 'break'
  sessionDuration: number
}

const moodOptions = [
  { score: 1, icon: HeartCrack, label: 'Very Bad', color: 'text-red-600', bg: 'bg-red-100 hover:bg-red-200' },
  { score: 2, icon: Frown, label: 'Bad', color: 'text-orange-600', bg: 'bg-orange-100 hover:bg-orange-200' },
  { score: 3, icon: Meh, label: 'Okay', color: 'text-yellow-600', bg: 'bg-yellow-100 hover:bg-yellow-200' },
  { score: 4, icon: Smile, label: 'Good', color: 'text-green-600', bg: 'bg-green-100 hover:bg-green-200' },
  { score: 5, icon: PartyPopper, label: 'Excellent', color: 'text-blue-600', bg: 'bg-blue-100 hover:bg-blue-200' },
]

const energyLevels = [
  { value: 1, label: 'Very Low' },
  { value: 2, label: 'Low' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'High' },
  { value: 5, label: 'Very High' },
]

const stressLevels = [
  { value: 1, label: 'Very Low' },
  { value: 2, label: 'Low' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'High' },
  { value: 5, label: 'Very High' },
]

export default function MoodTrackerModal({ 
  isOpen, 
  onClose, 
  sessionType, 
  sessionDuration 
}: MoodTrackerModalProps) {
  const isOnline = useNetworkStatus()
  const [selectedMood, setSelectedMood] = useState<number | null>(null)
  const [energyLevel, setEnergyLevel] = useState<number>(3)
  const [stressLevel, setStressLevel] = useState<number>(3)
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (selectedMood === null) return

    setIsSubmitting(true)

    try {
      const moodData: MoodData = {
        mood_score: selectedMood,
        energy_level: energyLevel,
        stress_level: stressLevel,
        notes: notes.trim() || undefined,
        tags: [sessionType, 'post-session', `${Math.round(sessionDuration / 60)}min`]
      }

      if (isOnline) {
        await api.createMood(moodData)
        // Try to sync any offline data
        await OfflineStorage.syncMoods()
        OfflineStorage.clearSyncedData()
      } else {
        OfflineStorage.storeMood(moodData)
      }

      onClose()
      resetForm()
    } catch (error) {
      console.error('Failed to submit mood:', error)
      // Store offline even if online submission failed
      OfflineStorage.storeMood({
        mood_score: selectedMood,
        energy_level: energyLevel,
        stress_level: stressLevel,
        notes: notes.trim() || undefined,
        tags: [sessionType, 'post-session', `${Math.round(sessionDuration / 60)}min`]
      })
      onClose()
      resetForm()
    } finally {
      setIsSubmitting(false)
    }
  }

  const resetForm = () => {
    setSelectedMood(null)
    setEnergyLevel(3)
    setStressLevel(3)
    setNotes('')
  }

  const handleClose = () => {
    onClose()
    resetForm()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              How are you feeling?
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              After your {sessionType} session ({Math.round(sessionDuration / 60)} minutes)
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Mood Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Overall Mood
            </label>
            <div className="grid grid-cols-5 gap-2">
              {moodOptions.map((mood) => {
                const Icon = mood.icon
                return (
                  <button
                    key={mood.score}
                    onClick={() => setSelectedMood(mood.score)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      selectedMood === mood.score
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : `border-gray-200 dark:border-gray-600 ${mood.bg} dark:hover:bg-gray-700`
                    }`}
                  >
                    <Icon className={`w-6 h-6 mx-auto ${mood.color}`} />
                    <div className="text-xs mt-1 text-gray-600 dark:text-gray-400">
                      {mood.label}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Energy Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Energy Level
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min="1"
                max="5"
                value={energyLevel}
                onChange={(e) => setEnergyLevel(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                {energyLevels.map((level) => (
                  <span key={level.value} className={energyLevel === level.value ? 'font-medium text-blue-600 dark:text-blue-400' : ''}>
                    {level.label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Stress Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Stress Level
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min="1"
                max="5"
                value={stressLevel}
                onChange={(e) => setStressLevel(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                {stressLevels.map((level) => (
                  <span key={level.value} className={stressLevel === level.value ? 'font-medium text-red-600 dark:text-red-400' : ''}>
                    {level.label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="How was your session? Any insights or thoughts?"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Network Status */}
          {!isOnline && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-3">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                You're offline. Your mood data will be saved locally and synced when you're back online.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Skip
          </button>
          <button
            onClick={handleSubmit}
            disabled={selectedMood === null || isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? 'Saving...' : 'Save Mood'}
          </button>
        </div>
      </div>
    </div>
  )
}
