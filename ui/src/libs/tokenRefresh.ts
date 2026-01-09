// src/libs/tokenRefresh.ts
import { useAuthStore } from './auth';
import { jwtDecode } from 'jwt-decode';

interface JWTPayload {
  exp: number;
  sub: string;
  role?: string;
}

/**
 * Démarre un timer pour rafraîchir le token avant expiration
 */
export function startTokenRefreshTimer() {
  const checkAndRefresh = async () => {
    const { accessToken, refreshAccessToken } = useAuthStore.getState();
    
    if (!accessToken) return;

    try {
      const decoded = jwtDecode<JWTPayload>(accessToken);
      const expiresAt = decoded.exp * 1000; // Convertir en ms
      const now = Date.now();
      const timeUntilExpiry = expiresAt - now;

      // Rafraîchir 5 minutes avant l'expiration
      if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) {
        console.log('⏰ Token expires soon, refreshing proactively...');
        await refreshAccessToken();
      }
    } catch (error) {
      console.error('Token refresh check failed:', error);
    }
  };

  // Vérifier toutes les minutes
  const interval = setInterval(checkAndRefresh, 60 * 1000);
  
  // Vérifier immédiatement au démarrage
  checkAndRefresh();

  // Retourner la fonction de cleanup
  return () => clearInterval(interval);
}
