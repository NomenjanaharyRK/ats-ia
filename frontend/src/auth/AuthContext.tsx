import React, { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin } from "../api/ats";

interface AuthUser {
  email: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
const [user, setUser] = useState<AuthUser | null>(null);
const [token, setToken] = useState<string | null>(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const storedToken = localStorage.getItem("ats_token");
  const storedEmail = localStorage.getItem("ats_email");
  if (storedToken && storedEmail) {
    setToken(storedToken);
    setUser({ email: storedEmail });
  }
  setLoading(false);
}, []);


  const login = async (email: string, password: string) => {
    const data = await apiLogin(email, password);
    localStorage.setItem("ats_token", data.access_token);
    localStorage.setItem("ats_email", email);
    setToken(data.access_token);
    setUser({ email });
  };

  const logout = () => {
    localStorage.removeItem("ats_token");
    localStorage.removeItem("ats_email");
    setToken(null);
    setUser(null);
  };

if (loading) {
  return <div className="min-h-screen flex items-center justify-center">Chargement...</div>;
}

return (
  <AuthContext.Provider value={{ user, token, login, logout }}>
    {children}
  </AuthContext.Provider>
);

};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
