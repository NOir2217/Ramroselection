import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { apiFetch } from "../utils/api";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { CheckCircle2, Circle, ArrowLeft } from "lucide-react";

const STAGES = [
  { key: 'pending_payment', label: 'Pending Payment' },
  { key: 'processing', label: 'Processing' },
  { key: 'ready_for_dispatch', label: 'Ready for Dispatch' },
  { key: 'out_for_delivery', label: 'Out for Delivery' },
  { key: 'delivered', label: 'Delivered' }
];

export function OrderTracking() {
  const { orderNumber } = useParams();
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrder();
  }, [orderNumber]);

  const loadOrder = async () => {
    try {
      const res = await apiFetch(`/api/orders/${orderNumber}/`);
      if (!res.ok) throw new Error("Order not found");
      const data = await res.json();
      setOrder(data);
    } catch (err) {
      toast.error("Failed to load order tracking");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading tracking info...</div>;
  if (!order) return <div className="p-8 text-center">Order not found.</div>;

  const currentStageIndex = STAGES.findIndex(s => s.key === order.status);
  
  // Special states that break the normal flow
  const isCancelled = order.status === 'cancelled';
  const isReturned = order.status === 'returned';
  const isExchanged = order.status === 'exchanged';

  return (
    <div className="container mx-auto px-4 py-12 max-w-3xl min-h-[calc(100vh-10rem)]">
      <Link to="/account" className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="h-4 w-4 mr-1" /> Back to Account
      </Link>
      
      <div className="bg-card border border-border rounded-lg p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-border">
          <div>
            <h1 className="text-2xl font-bold">Order {order.order_number}</h1>
            <p className="text-sm text-muted-foreground mt-1">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
          </div>
          <div className="mt-4 md:mt-0 text-right">
            <p className="font-medium text-lg">Total: NRS {order.total}</p>
          </div>
        </div>

        {isCancelled || isReturned || isExchanged ? (
          <div className="p-6 bg-secondary rounded-lg text-center">
            <h3 className="text-xl font-bold text-destructive uppercase tracking-widest">{order.status}</h3>
            <p className="text-muted-foreground mt-2">This order is no longer in the standard delivery pipeline.</p>
          </div>
        ) : (
          <div className="relative">
            {/* Desktop Horizontal Line */}
            <div className="hidden md:block absolute top-5 left-8 right-8 h-1 bg-muted -z-10" />
            <div 
              className="hidden md:block absolute top-5 left-8 h-1 bg-primary -z-10 transition-all duration-500" 
              style={{ width: `${Math.max(0, (currentStageIndex / (STAGES.length - 1)) * 100 - 10)}%` }}
            />

            <div className="flex flex-col md:flex-row justify-between gap-6 md:gap-0">
              {STAGES.map((stage, idx) => {
                const isCompleted = idx <= currentStageIndex;
                const isCurrent = idx === currentStageIndex;
                
                return (
                  <div key={stage.key} className="flex md:flex-col items-center gap-4 md:gap-2">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-card border-2 transition-colors ${isCompleted ? 'border-primary text-primary' : 'border-muted text-muted-foreground'}`}>
                      {isCompleted ? <CheckCircle2 className="h-6 w-6" /> : <Circle className="h-4 w-4" />}
                    </div>
                    <div className="md:text-center">
                      <p className={`font-medium text-sm ${isCurrent ? 'text-primary font-bold' : isCompleted ? 'text-foreground' : 'text-muted-foreground'}`}>
                        {stage.label}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-12">
          <h3 className="font-bold text-lg mb-4">Items in this order</h3>
          <div className="space-y-4">
            {order.items.map((item: any) => (
              <div key={item.id} className="flex justify-between items-center py-2 border-b border-border/50 last:border-0">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-muted rounded overflow-hidden">
                    <img src={item.variant.product.image} alt={item.variant.product.name} className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <p className="font-medium">{item.variant.product.name}</p>
                    <p className="text-sm text-muted-foreground">Qty: {item.quantity}</p>
                  </div>
                </div>
                <p className="font-medium">NRS {item.unit_price}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
