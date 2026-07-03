import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "sonner";
import { ArrowRight, Clock, User } from "lucide-react";

interface OrderItem {
  id: number;
  variant: {
    product: { name: string; image: string };
    size: string;
    color: string;
    shade: string;
  };
  quantity: number;
  unit_price: number;
}

interface Order {
  id: number;
  order_number: string;
  customer: { email: string; user: { username: string } } | null;
  guest_email: string | null;
  status: string;
  total: number;
  created_at: string;
  items: OrderItem[];
}

const COLUMNS = [
  { key: "pending_payment", label: "Pending Payment", color: "border-yellow-400 bg-yellow-50" },
  { key: "processing", label: "Processing", color: "border-blue-400 bg-blue-50" },
  { key: "ready_for_dispatch", label: "Ready for Dispatch", color: "border-indigo-400 bg-indigo-50" },
  { key: "out_for_delivery", label: "Out for Delivery", color: "border-purple-400 bg-purple-50" },
  { key: "delivered", label: "Delivered", color: "border-green-400 bg-green-50" },
  { key: "cancelled", label: "Cancelled", color: "border-red-400 bg-red-50" },
];

const STATUS_OPTIONS = [
  "pending_payment", "processing", "ready_for_dispatch",
  "out_for_delivery", "delivered", "returned", "exchanged", "cancelled",
];

const STATUS_LABELS: Record<string, string> = {
  pending_payment: "Pending Payment",
  processing: "Processing",
  ready_for_dispatch: "Ready for Dispatch",
  out_for_delivery: "Out for Delivery",
  delivered: "Delivered",
  returned: "Returned",
  exchanged: "Exchanged",
  cancelled: "Cancelled",
};

export function OrdersKanban() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = useCallback(() => {
    apiFetch("/api/orders/admin/orders/")
      .then((res) => res.json())
      .then((data) => {
        setOrders(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const moveOrder = async (orderId: number, newStatus: string) => {
    try {
      const res = await apiFetch(`/api/orders/admin/orders/${orderId}/status/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        toast.success(`Order moved to ${STATUS_LABELS[newStatus]}`);
        fetchOrders();
      } else {
        toast.error("Failed to update order status");
      }
    } catch {
      toast.error("Network error");
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Orders Pipeline</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="space-y-3 animate-pulse">
              <div className="h-10 bg-muted rounded" />
              {[...Array(2)].map((_, j) => (
                <div key={j} className="h-24 bg-muted rounded" />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Orders Pipeline</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 overflow-x-auto">
        {COLUMNS.map((col) => {
          const colOrders = orders.filter((o) => o.status === col.key);
          return (
            <div key={col.key} className={`min-w-[250px] rounded-lg border-2 ${col.color} p-3`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm">{col.label}</h3>
                <Badge variant="secondary">{colOrders.length}</Badge>
              </div>

              <div className="space-y-3 max-h-[60vh] overflow-y-auto">
                {colOrders.map((order) => (
                  <Card key={order.id} className="p-3 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-semibold">{order.order_number}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(order.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
                      <User className="h-3 w-3" />
                      {order.customer?.user?.username ?? order.guest_email ?? "Guest"}
                    </div>

                    <div className="text-sm font-semibold mb-2">NRS {order.total.toLocaleString()}</div>

                    <div className="text-xs text-muted-foreground mb-3">
                      {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                    </div>

                    {col.key !== "delivered" && col.key !== "cancelled" && (
                      <Select
                        value={order.status}
                        onValueChange={(val) => moveOrder(order.id, val)}
                      >
                        <SelectTrigger className="h-7 text-xs" onClick={(e) => e.stopPropagation()}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {STATUS_OPTIONS.map((s) => (
                            <SelectItem key={s} value={s} className="text-xs">
                              {STATUS_LABELS[s]}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </Card>
                ))}

                {colOrders.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-4">No orders</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
