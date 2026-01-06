import { create } from "zustand"
import { persist } from "zustand/middleware"
import api from "@/lib/api"

interface User {
  id: number
  email: string
  name?: string
  role: string
}

interface AuthStore {
  token: string | null
  user: User | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthStore>(
  persist(
    (set) => ({
      token: null,
      user: null,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post("/auth/login", { email, password })
          const { access_token, user } = response.data
          
          localStorage.setItem("token", access_token)
          set({ token: access_token, user, isLoading: false })
        } catch (error: any) {
          const message = error.response?.data?.detail || "Login failed"
          set({ error: message, isLoading: false })
          throw error
        }
      },
      
      logout: () => {
        localStorage.removeItem("token")
        set({ token: null, user: null, error: null })
      },
      
      setToken: (token: string) => {
        localStorage.setItem("token", token)
        set({ token })
      },
      
      setUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
