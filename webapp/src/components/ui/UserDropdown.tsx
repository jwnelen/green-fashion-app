import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'

export default function UserDropdown() {
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)

  if (!user) return null

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md transition-colors"
      >
        {user.picture ? (
          <img
            src={user.picture}
            alt={user.name || 'User avatar'}
            className="h-8 w-8 rounded-full object-cover"
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
