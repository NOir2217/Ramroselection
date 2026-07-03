import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate, useLocation } from "react-router";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
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
    // On mount, silently try to refresh token using HttpOnly cookie
    let active = true;
    
    fetch("/api/auth/token/refresh/", {
      method: "POST",
    })
      .then(res => {
        if (!res.ok) throw new Error("No session");
        return res.json();
      })
      .then(data => {
        if (active) {
          setAccessToken(data.access);
          // If we had a user endpoint we'd fetch it here.
          // For now we will rely on decoding the JWT if needed, or simply let the app know we are authed.
          // In a real app we'd fetch /api/auth/me/ to get full user details.
          setUser({ id: 1, email: "user@example.com", first_name: "User", last_name: "", is_staff: false }); // Mock user
        }
      })
      .catch(() => {
        if (active) {
          setAccessToken(null);
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
    if (userData) {
      setUser(userData);
    } else {
      setUser({ id: 1, email: "user@example.com", first_name: "User", last_name: "", is_staff: false });
    }
  };

  const logout = async () => {
    try {
      await fetch("/api/auth/token/logout/", { method: "POST" });
    } catch (e) {
      console.error("Logout error", e);
    } finally {
      setAccessToken(null);
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
