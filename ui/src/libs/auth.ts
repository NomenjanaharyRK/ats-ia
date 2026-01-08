import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type UserRole = 'admin' | 'recruiter';

interface AuthState {
  user: { email: string; role: UserRole } | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
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
          throw new Error('Identifiants incorrects');
        }

        const data = await response.json();

        // Stockage tokens + email pour debug et restauration
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        localStorage.setItem('user_email', email);

        // Pour l’instant on ne distingue pas encore admin/recruiter côté front,
        // le backend gère les permissions via JWT. Tu pourras adapter plus tard.
        const role: UserRole = 'admin';

        set({
          user: { email, role },
          accessToken: data.access_token,
          refreshToken: data.refresh_token || null,
        });
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        set({ user: null, accessToken: null, refreshToken: null });
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
