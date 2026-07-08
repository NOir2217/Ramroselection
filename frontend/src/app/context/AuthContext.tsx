import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate, useLocation } from "react-router";
import { API_BASE_URL } from "@/config";
import { setAccessTokenInMemory } from "../utils/api";

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  profile?: any;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (access: string, user?: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    let active = true;

    fetch(`${API_BASE_URL}/api/auth/token/refresh/`, {
      method: "POST",
      credentials: "include",
    })
      .then(res => {
        if (!res.ok) throw new Error("No session");
        return res.json();
      })
      .then(data => {
        if (active) {
          setAccessToken(data.access);
          setAccessTokenInMemory(data.access);
          if (data.user) {
            setUser(data.user);
          } else {
            setUser(null);
          }
        }
      })
      .catch(() => {
        if (active) {
          setAccessToken(null);
          setAccessTokenInMemory(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => { active = false; };
  }, []);

  const login = (access: string, userData?: User) => {
    setAccessToken(access);
    setAccessTokenInMemory(access);
    if (userData) {
      setUser(userData);
    } else {
      setUser(null);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/auth/token/logout/`, { 
        method: "POST",
        headers: {
          "Authorization": `Bearer ${accessToken}`
        },
        credentials: "include"
      });
    } catch (e) {
      console.error("Logout error", e);
    } finally {
      setAccessToken(null);
      setAccessTokenInMemory(null);
      setUser(null);
      navigate("/login");
    }
  };


  return (
    <AuthContext.Provider value={{ user, accessToken, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
