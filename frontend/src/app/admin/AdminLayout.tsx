import { useAuth } from "../context/AuthContext";
import { Navigate, Outlet, Link, useLocation } from "react-router";
import {
  LogOut, LayoutDashboard, ShoppingBag, Users, Settings,
  Package, AlertTriangle, ImageIcon, MessageSquare, Skull, Grid,
  Percent, ShoppingCart, BarChart3
} from "lucide-react";
import { Button } from "../components/ui/button";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { to: "/admin/orders", label: "Orders", icon: ShoppingBag },
  { to: "/admin/low-stock", label: "Low Stock", icon: AlertTriangle },
  { to: "/admin/expiring", label: "Expiring", icon: Skull },
  { to: "/admin/variants", label: "Variants", icon: Package },
  { to: "/admin/images", label: "Images", icon: ImageIcon },
  { to: "/admin/collections", label: "Collections", icon: Grid },
  { to: "/admin/discounts", label: "Discounts", icon: Percent },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/admin/abandoned-carts", label: "Abandoned Carts", icon: ShoppingCart },
  { to: "/admin/reviews", label: "Reviews", icon: MessageSquare },
];

export function AdminLayout() {
  const { user, isLoading, logout } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="p-8 text-center h-screen flex items-center justify-center">Loading admin...</div>;
  }

  if (!user || !user.is_staff) {
    return <Navigate to="/login" replace />;
  }

  const isActive = (path: string) => {
    if (path === "/admin") return location.pathname === "/admin";
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-muted/20 flex flex-col md:flex-row">
      <aside className="w-full md:w-64 bg-card border-r border-border min-h-screen p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8 px-2">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
            <span className="text-primary-foreground font-bold">R</span>
          </div>
          <span className="font-bold text-lg">Admin Panel</span>
        </div>

        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive(item.to)
                  ? "bg-secondary text-secondary-foreground font-medium"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="pt-4 border-t border-border mt-auto">
          <div className="px-3 mb-4">
            <p className="text-sm font-medium truncate">{user.email}</p>
            <p className="text-xs text-muted-foreground">Admin</p>
          </div>
          <Button variant="outline" className="w-full justify-start gap-2" onClick={logout}>
            <LogOut className="h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
