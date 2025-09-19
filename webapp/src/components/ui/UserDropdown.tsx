import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { API_VERSION } from '../../lib/api'

export default function UserDropdown() {
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [imgError, setImgError] = useState(false)

  const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + "/" + API_VERSION

  if (!user) return null

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md transition-colors"
      >
        {user.picture && !imgError ? (
          <img
            src={user.picture.startsWith('http') ? `${API_BASE_URL}/proxy/avatar?url=${encodeURIComponent(user.picture)}` : user.picture}
            alt={user.name || 'User avatar'}
            className="h-8 w-8 rounded-full object-cover"
            referrerPolicy="no-referrer"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="h-8 w-8 rounded-full bg-gray-400 flex items-center justify-center text-white font-medium text-sm">
            {user.name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
        )}
        <ChevronDown className="cursor-pointer h-4 w-4" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
            <div className="py-1">
              <div className="px-4 py-2 text-sm text-gray-900 font-medium">
                {user.name}
              </div>
              <hr className="border-gray-200" />
              <button
                onClick={() => {
                  logout()
                  setIsOpen(false)
                }}
                className="cursor-pointer block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
