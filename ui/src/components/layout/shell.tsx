import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/libs/auth';
import { Button } from '@/components/ui/button';

export function Shell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { logout, user } = useAuthStore();

  // Détermine si une route est active
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-background font-sans antialiased flex">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-card shadow-lg transform transition-transform duration-200 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:inset-0 flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/75 bg-clip-text text-transparent">
            ATS-IA
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Scoring IA de CV
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
          {/* Dashboard */}
          <Link
            to="/dashboard"
            onClick={() => setSidebarOpen(false)}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all ${
              isActive('/dashboard')
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-foreground'
            }`}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Dashboard</span>
          </Link>

          {/* Offres */}
          <Link
            to="/offers"
            onClick={() => setSidebarOpen(false)}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all ${
              isActive('/offers') || location.pathname.startsWith('/offers/')
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-foreground'
            }`}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m-1 4h1m4-4h1m-1 4h1m-5-4h5m0 0h1"
              />
            </svg>
            <span>Offres</span>
          </Link>

          {/* Candidatures */}
          <Link
            to="/applications"
            onClick={() => setSidebarOpen(false)}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all ${
              isActive('/applications')
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-foreground'
            }`}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>Candidatures</span>
          </Link>
        </nav>

        {/* Footer avec user info */}
        <div className="p-6 border-t border-border space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/60 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">
                {user?.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.email}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {user?.role}
              </p>
            </div>
          </div>
          <Button
            onClick={() => {
              logout();
              setSidebarOpen(false);
            }}
            variant="outline"
            size="sm"
            className="w-full"
          >
            Déconnexion
          </Button>
        </div>
      </div>

      {/* Overlay pour mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden bg-black/50"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Contenu principal */}
      <div className="lg:ml-0 w-full lg:flex-1">
        {/* Topbar */}
        <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
          <div className="h-16 px-6 flex items-center justify-between">
            {/* Menu button mobile */}
            <button
              className="lg:hidden p-2 rounded-md hover:bg-accent transition-colors"
              onClick={() => setSidebarOpen(true)}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* Spacer */}
            <div className="flex-1" />

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/60 rounded-full flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity">
                <span className="text-white text-sm font-bold">
                  {user?.email?.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm font-medium text-foreground hidden sm:block">
                {user?.email}
              </span>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
