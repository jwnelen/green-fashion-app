export type AuthToken = string

export interface DecodedUser {
  sub: string
  email: string
  name?: string
  picture?: string
  exp?: number
  [key: string]: unknown
}

export interface AuthContextType {
  user: DecodedUser | null
  saveToken: (token: AuthToken) => void
  getToken: () => AuthToken | null
  removeToken: () => void
  logout: () => void
  isTokenExpired: (token: AuthToken) => boolean
  getUserFromToken: () => DecodedUser | null
  getUser: () => DecodedUser | null
}
