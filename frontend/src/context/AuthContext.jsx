// AuthContext.jsx — Global auth state management
// React Context lets us share data across ALL components
// without passing props through every level
// Think of it as a global variable that React manages

import { createContext, useContext, useState } from "react"

// Create the context — like creating a "channel" to share data
const AuthContext = createContext()

export function AuthProvider({ children }) {
  // token and user stored in state
  // useState(localStorage.getItem("token")) means:
  // "when app loads, check if token already exists in browser storage"
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [user, setUser] = useState(null)

  // login — saves token to state AND localStorage
  // localStorage persists even after page refresh
  const login = (accessToken) => {
    localStorage.setItem("token", accessToken)
    setToken(accessToken)
  }

  // logout — removes token from everywhere
  const logout = () => {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
  }

  // isAuthenticated — true if token exists
  const isAuthenticated = !!token

  return (
    // Provider wraps the entire app — any component inside
    // can access token, login, logout via useAuth()
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook — makes it easy to use auth in any component
// Instead of: const { token } = useContext(AuthContext)
// We write: const { token } = useAuth()
export function useAuth() {
  return useContext(AuthContext)
}