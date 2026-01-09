import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/libs/auth';
import { Button } from '@/components/ui/button';

export function Login() {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('adminpassword');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const login = useAuthStore((state) => state.login);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const location = useLocation();

  // Redirige si déjà connecté
  if (user) {
    const from = location.state?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
    return null;
  }
  

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-primary/75 to-secondary bg-clip-text text-transparent mb-2">
            ATS-IA
          </h1>
          <p className="text-muted-foreground">Plateforme d'analyse IA de CV</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-card p-8 rounded-2xl shadow-2xl border space-y-6">
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-xl text-destructive text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium mb-2 text-foreground">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-input rounded-xl bg-background focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-foreground"
              placeholder="admin@example.com"
              disabled={loading}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-foreground">Mot de passe</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-input rounded-xl bg-background focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-foreground"
              placeholder="••••••••"
              disabled={loading}
              required
            />
          </div>

          <Button 
            type="submit" 
            className="w-full h-12 text-lg font-semibold"
            disabled={loading}
          >
            {loading ? (
              <>
                <svg className="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" pathLength="0" className="opacity-25" />
                  <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Connexion...
              </>
            ) : (
              'Se connecter'
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
