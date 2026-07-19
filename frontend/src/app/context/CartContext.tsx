import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { apiFetch } from "../utils/api";
import { toast } from "sonner";

interface CartItem {
  id: number;
  quantity: number;
  line_total: string;
  variant: {
    id: number;
    size: string | null;
    color: string | null;
    shade: string | null;
    product: {
      id: number;
      name: string;
      image: string;
      price: number;
    };
  };
}

interface Cart {
  id: string;
  items: CartItem[];
  subtotal: string;
}

interface CartContextType {
  cart: Cart | null;
  itemCount: number;
  isLoading: boolean;
  fetchCart: () => Promise<void>;
  addToCart: (variantId: number, quantity?: number) => Promise<boolean>;
  updateQuantity: (itemId: number, newQuantity: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  mergeGuestCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCart = useCallback(async () => {
    try {
      const res = await apiFetch("/api/cart/");
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      // Silent fail — cart fetch is best-effort
    }
  }, []);

  // Fetch cart on mount
  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = useCallback(async (variantId: number, quantity = 1): Promise<boolean> => {
    setIsLoading(true);
    try {
      const res = await apiFetch("/api/cart/items/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variantId, quantity }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to add item to cart.");
        return false;
      }

      const updatedCart = await res.json();
      setCart(updatedCart);
      toast.success("Added to cart!");
      return true;
    } catch (err) {
      toast.error("Network error — could not add to cart.");
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateQuantity = useCallback(async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      const res = await apiFetch(`/api/cart/items/${itemId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity: newQuantity }),
      });
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      toast.error("Failed to update quantity.");
    }
  }, []);

  const removeItem = useCallback(async (itemId: number) => {
    try {
      const res = await apiFetch(`/api/cart/items/${itemId}/`, {
        method: "DELETE",
      });
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      toast.error("Failed to remove item.");
    }
  }, []);

  /** Call after login to merge the guest cart into the authenticated user's cart. */
  const mergeGuestCart = useCallback(async () => {
    try {
      const res = await apiFetch("/api/cart/merge/", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      // Non-fatal — swallow silently
    }
  }, []);

  const itemCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) ?? 0;

  return (
    <CartContext.Provider value={{ cart, itemCount, isLoading, fetchCart, addToCart, updateQuantity, removeItem, mergeGuestCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}
