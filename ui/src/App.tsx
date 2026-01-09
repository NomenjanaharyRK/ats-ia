import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { Shell } from '@/components/layout/shell';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { OffersPage } from '@/pages/Offers';
import { CreateOfferPage } from '@/pages/CreateOffer';
import { OfferDetail } from '@/pages/OfferDetail';
import { ApplicationsPage } from '@/pages/ApplicationsPage';
import { useAuthStore } from '@/libs/auth';
import { startTokenRefreshTimer } from '@/libs/tokenRefresh'; // ✅ NOUVEAU
import './index.css';
import { useEffect } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuthStore();
  const location = useLocation();

  const tokenFromStorage = localStorage.getItem('access_token');
  const isAuthenticated = Boolean(
    (user && accessToken) || tokenFromStorage
  );

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Shell>{children}</Shell>;
}

function AppContent() {
  return (
    <Router>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen">
          <Routes>
            {/* Pages publiques */}
            <Route path="/login" element={<Login />} />

            {/* Pages protégées */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/offers"
              element={
                <ProtectedRoute>
                  <OffersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/offers/new"
              element={
                <ProtectedRoute>
                  <CreateOfferPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/offers/:id"
              element={
                <ProtectedRoute>
                  <OfferDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/applications"
              element={
                <ProtectedRoute>
                  <ApplicationsPage />
                </ProtectedRoute>
              }
            />

            {/* Redirections */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>

          {/* DevTools + Toasts */}
          <ReactQueryDevtools initialIsOpen={false} />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'hsl(var(--card))',
                color: 'hsl(var(--foreground))',
                border: '1px solid hsl(var(--border))',
              },
            }}
          />
        </div>
      </QueryClientProvider>
    </Router>
  );
}

function App() {
  useEffect(() => {
    // ✅ Démarrer le timer de refresh proactif
    // Rafraîchit le token 5 minutes avant expiration
    const cleanup = startTokenRefreshTimer();
    
    return () => {
      // ✅ Cleanup au démontage du composant
      cleanup();
    };
  }, []);

  return <AppContent />;
}

export default App;
