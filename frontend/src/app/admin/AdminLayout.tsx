import { useAuth } from "../context/AuthContext";
import { Navigate, Outlet, Link } from "react-router";
import { LogOut, LayoutDashboard, Settings, ShoppingBag, Users } from "lucide-react";
import { Button } from "../components/ui/button";

export function AdminLayout() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div className="p-8 text-center h-screen flex items-center justify-center">Loading admin...</div>;
  }

  if (!user || !user.is_staff) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-muted/20 flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-card border-r border-border min-h-screen p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8 px-2">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
            <span className="text-primary-foreground font-bold">R</span>
          </div>
          <span className="font-bold text-lg">Admin Panel</span>
        </div>

        <nav className="flex-1 space-y-2">
          <Link to="/admin" className="flex items-center gap-3 px-3 py-2 rounded-md bg-secondary text-secondary-foreground font-medium">
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
          <Link to="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
            <ShoppingBag className="h-4 w-4" />
            Orders
          </Link>
          <Link to="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
            <Users className="h-4 w-4" />
            Customers
          </Link>
          <Link to="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
            <Settings className="h-4 w-4" />
            Settings
          </Link>
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

      {/* Main Content Area */}
      <main className="flex-1 p-8">
        <Outlet />
        
        {/* Placeholder dashboard content if Outlet is empty */}
        <div className="space-y-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {['Total Sales', 'Active Orders', 'New Customers', 'Low Stock'].map((stat, i) => (
              <div key={i} className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-sm font-medium text-muted-foreground mb-2">{stat}</h3>
                <p className="text-2xl font-bold">--</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
