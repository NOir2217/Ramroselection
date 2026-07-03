import { X, Trash2, ShoppingBag } from "lucide-react";
import { Button } from "./ui/button";
import { useEffect, useState } from "react";
import { Link } from "react-router";

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const [cart, setCart] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchCart = () => {
    setLoading(true);
    fetch('http://127.0.0.1:8000/api/cart/')
      .then(res => res.json())
      .then(data => {
        setCart(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchCart();
    }
  }, [isOpen]);

  const updateQuantity = (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    fetch(`http://127.0.0.1:8000/api/cart/items/${itemId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: newQuantity })
    })
    .then(res => res.json())
    .then(data => setCart(data));
  };

  const removeItem = (itemId: number) => {
    fetch(`http://127.0.0.1:8000/api/cart/items/${itemId}/`, {
      method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => setCart(data));
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 z-50 transition-opacity"
        onClick={onClose}
      />
      <div className="fixed inset-y-0 right-0 w-full max-w-md bg-background shadow-xl z-50 flex flex-col transform transition-transform duration-300">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <ShoppingBag className="w-5 h-5" />
            Your Cart
          </h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          {loading ? (
            <p className="text-center text-muted-foreground mt-10">Loading...</p>
          ) : !cart?.items?.length ? (
            <div className="flex flex-col items-center justify-center flex-1 text-muted-foreground">
              <ShoppingBag className="w-12 h-12 mb-4 opacity-20" />
              <p>Your cart is empty.</p>
              <Button variant="outline" className="mt-4" onClick={onClose}>Continue Shopping</Button>
            </div>
          ) : (
            cart.items.map((item: any) => (
              <div key={item.id} className="flex gap-4 p-3 border rounded-lg bg-card">
                <img 
                  src={item.variant.product?.image || "https://placehold.co/150"} 
                  alt={item.variant.product?.name} 
                  className="w-20 h-24 object-cover rounded-md"
                />
                <div className="flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="font-medium line-clamp-2 text-sm">{item.variant.product?.name || "Product Name"}</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {item.variant.size && `Size: ${item.variant.size} `}
                      {item.variant.color && `Color: ${item.variant.color}`}
                    </p>
                    <p className="font-semibold mt-1">NRS {item.line_total}</p>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center border rounded-md">
                      <button 
                        className="px-2 py-1 text-muted-foreground hover:text-foreground"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      >-</button>
                      <span className="px-2 text-sm font-medium">{item.quantity}</span>
                      <button 
                        className="px-2 py-1 text-muted-foreground hover:text-foreground"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >+</button>
                    </div>
                    <Button variant="ghost" size="icon" className="text-destructive h-8 w-8" onClick={() => removeItem(item.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {cart?.items?.length > 0 && (
          <div className="border-t p-4 bg-muted/30">
            <div className="flex justify-between items-center mb-4">
              <span className="font-semibold">Subtotal</span>
              <span className="font-bold text-lg">NRS {cart.subtotal}</span>
            </div>
            <Link to="/checkout" onClick={onClose} className="block w-full">
              <Button className="w-full h-12 text-lg font-medium">
                Proceed to Checkout
              </Button>
            </Link>
          </div>
        )}
      </div>
    </>
  );
}
