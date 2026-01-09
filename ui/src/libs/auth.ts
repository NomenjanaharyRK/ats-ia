import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type UserRole = 'admin' | 'recruiter';

interface AuthState {
  user: { email: string; role: UserRole } | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      login: async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/login`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Identifiants incorrects');
        }

        const data = await response.json();

        // Stockage tokens + email
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        localStorage.setItem('user_email', email);

        // Déterminer le rôle (vous pouvez le décoder du JWT si besoin)
        const role: UserRole = 'admin'; // À améliorer avec décodage JWT

        set({
          user: { email, role },
          accessToken: data.access_token,
          refreshToken: data.refresh_token || null,
        });

        console.log('✅ Login successful, tokens stored');
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        set({ user: null, accessToken: null, refreshToken: null });
        console.log('👋 Logged out');
      },

      // Fonction pour refresh manuel (utilisée par l'interceptor)
      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        console.log('🔄 Manually refreshing token...');

        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/refresh`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          }
        );

        if (!response.ok) {
          throw new Error('Failed to refresh token');
        }

        const data = await response.json();

        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        set({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        });

        console.log('✅ Token refreshed manually');
      },
    }),
    {
      name: 'ats-ia-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
