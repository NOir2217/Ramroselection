import { useAuth } from "../context/AuthContext";
import { Navigate, Link } from "react-router";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";
import { toast } from "sonner";

export function MyAccount() {
  const { user, isLoading, logout } = useAuth();
  const [orders, setOrders] = useState<any[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(true);

  useEffect(() => {
    if (user) {
      loadOrders();
    }
  }, [user]);

  const loadOrders = async () => {
    try {
      const res = await apiFetch("/api/orders/");
      const data = await res.json();
      setOrders(data);
    } catch (err) {
      toast.error("Failed to load orders");
    } finally {
      setLoadingOrders(false);
    }
  };

  const handleReturnRequest = async (itemId: number) => {
    const reason = window.prompt("Please provide a reason for return:");
    if (!reason) return;

    try {
      const res = await apiFetch(`/api/orders/items/${itemId}/return/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Return request failed");
      }
      toast.success("Return requested successfully");
      loadOrders(); // reload to show updated status
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  if (isLoading) return <div className="p-8 text-center">Loading profile...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">My Account</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <Button variant="outline" className="w-full mt-4" onClick={logout}>
                Log out
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Order History</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingOrders ? (
                <p>Loading orders...</p>
              ) : orders.length === 0 ? (
                <p className="text-muted-foreground text-sm">You haven't placed any orders yet.</p>
              ) : (
                <div className="space-y-6">
                  {orders.map(order => (
                    <div key={order.id} className="border border-border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-4 border-b border-border pb-4">
                        <div>
                          <p className="font-bold text-lg">Order #{order.order_number}</p>
                          <p className="text-sm text-muted-foreground">{new Date(order.created_at).toLocaleDateString()}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">NRS {order.total}</p>
                          <span className="inline-block px-2 py-1 bg-secondary text-xs rounded-md uppercase mt-1 tracking-wider">
                            {order.status.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        {order.items.map((item: any) => {
                          const hasReturn = item.return_requests && item.return_requests.length > 0;
                          const returnStatus = hasReturn ? item.return_requests[0].status : null;
                          
                          return (
                            <div key={item.id} className="flex justify-between items-center">
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-muted rounded overflow-hidden">
                                  <img src={item.variant.product.image} alt="product" className="w-full h-full object-cover" />
                                </div>
                                <div>
                                  <p className="font-medium text-sm">{item.variant.product.name}</p>
                                  <p className="text-xs text-muted-foreground">Qty: {item.quantity}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                {order.status === 'delivered' && !hasReturn && (
                                  <Button variant="outline" size="sm" onClick={() => handleReturnRequest(item.id)}>
                                    Request Return
                                  </Button>
                                )}
                                {hasReturn && (
                                  <span className="text-xs text-orange-500 border border-orange-200 bg-orange-50 px-2 py-1 rounded">
                                    Return {returnStatus}
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      
                      <div className="mt-4 pt-4 border-t border-border">
                        <Link to={`/orders/${order.order_number}`}>
                          <Button variant="secondary" className="w-full">Track Order</Button>
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
