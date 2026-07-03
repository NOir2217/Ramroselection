import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ShoppingBag, Users, DollarSign, AlertTriangle, Package, Clock } from "lucide-react";

interface DashboardStats {
  totalOrders: number;
  recentOrders: number;
  totalRevenue: number;
  totalCustomers: number;
  pendingReturns: number;
  ordersByStatus: Record<string, number>;
}

export function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/orders/admin/dashboard/")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="p-6 animate-pulse">
              <div className="h-4 bg-muted rounded w-24 mb-3" />
              <div className="h-8 bg-muted rounded w-16" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const statCards = [
    { title: "Total Revenue", value: `NRS ${stats?.totalRevenue?.toLocaleString() ?? 0}`, icon: DollarSign, color: "text-green-600" },
    { title: "Total Orders", value: stats?.totalOrders ?? 0, icon: ShoppingBag, color: "text-blue-600" },
    { title: "Customers", value: stats?.totalCustomers ?? 0, icon: Users, color: "text-purple-600" },
    { title: "Pending Returns", value: stats?.pendingReturns ?? 0, icon: AlertTriangle, color: "text-orange-600" },
  ];

  const statusColors: Record<string, string> = {
    pending_payment: "bg-yellow-100 text-yellow-800",
    processing: "bg-blue-100 text-blue-800",
    ready_for_dispatch: "bg-indigo-100 text-indigo-800",
    out_for_delivery: "bg-purple-100 text-purple-800",
    delivered: "bg-green-100 text-green-800",
    returned: "bg-orange-100 text-orange-800",
    exchanged: "bg-cyan-100 text-cyan-800",
    cancelled: "bg-red-100 text-red-800",
  };

  const statusLabels: Record<string, string> = {
    pending_payment: "Pending Payment",
    processing: "Processing",
    ready_for_dispatch: "Ready for Dispatch",
    out_for_delivery: "Out for Delivery",
    delivered: "Delivered",
    returned: "Returned",
    exchanged: "Exchanged",
    cancelled: "Cancelled",
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <Card key={i} className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">{stat.title}</h3>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <p className="text-2xl font-bold">{stat.value}</p>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Package className="h-5 w-5" />
          Orders by Status
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(stats?.ordersByStatus ?? {}).map(([status, count]) => (
            <div key={status} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <Badge variant="secondary" className={statusColors[status] ?? ""}>
                {statusLabels[status] ?? status}
              </Badge>
              <span className="font-semibold text-lg">{count}</span>
            </div>
          ))}
          {Object.keys(stats?.ordersByStatus ?? {}).length === 0 && (
            <p className="col-span-4 text-muted-foreground text-sm">No orders yet.</p>
          )}
        </div>
      </Card>
    </div>
  );
}
