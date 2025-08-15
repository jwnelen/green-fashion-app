import React, { useCallback, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { jwtDecode } from 'jwt-decode'
import { googleLogout } from '@react-oauth/google'
import type { AuthToken, DecodedUser, AuthContextType } from '../types/auth'
import { AuthContext } from './auth-context'

const SESSION_KEY = 'googleToken'

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<DecodedUser | null>(null)

  // Initialize user state from sessionStorage on mount
  useEffect(() => {
    const token = sessionStorage.getItem(SESSION_KEY)
    if (token && !isTokenExpiredStatic(token)) {
      try {
        const decodedUser = jwtDecode<DecodedUser>(token)
        setUser(decodedUser)
      } catch (error) {
        console.error('Failed to decode stored token:', error)
        sessionStorage.removeItem(SESSION_KEY)
      }
    }
  }, [])

  const isTokenExpiredStatic = (token: AuthToken): boolean => {
    try {
      const decoded = jwtDecode<DecodedUser>(token)
      if (!decoded.exp) return true
      const nowInSeconds = Math.floor(Date.now() / 1000)
      return decoded.exp < nowInSeconds
    } catch {
      return true
    }
  }

  const saveToken = useCallback((token: AuthToken): void => {
    sessionStorage.setItem(SESSION_KEY, token)
    try {
      const decodedUser = jwtDecode<DecodedUser>(token)
      setUser(decodedUser)
      console.log('User logged in successfully:', decodedUser.name || decodedUser.email)
    } catch (error) {
      console.error('Failed to decode token:', error)
      setUser(null)
    }
  }, [])

  const getToken = useCallback((): AuthToken | null => {
    return sessionStorage.getItem(SESSION_KEY)
  }, [])

  const removeToken = useCallback((): void => {
    sessionStorage.removeItem(SESSION_KEY)
    setUser(null)
  }, [])

  const logout = useCallback(() => {
    googleLogout()
    removeToken()
  }, [removeToken])

  const isTokenExpired = useCallback((token: AuthToken): boolean => {
    return isTokenExpiredStatic(token)
  }, [])

  const getUser = useCallback((): DecodedUser | null => {
    return user
  }, [user])

  const getUserFromToken = useCallback((): DecodedUser | null => {
    const token = getToken()
    if (!token || isTokenExpired(token)) {
      removeToken()
      return null
    }
    try {
      return jwtDecode<DecodedUser>(token)
    } catch {
      return null
    }
  }, [getToken, isTokenExpired, removeToken])

  const value: AuthContextType = {
    user,
    saveToken,
    getToken,
    removeToken,
    logout,
    isTokenExpired,
    getUserFromToken,
    getUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
