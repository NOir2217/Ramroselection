import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { apiFetch } from "../utils/api";

interface WishlistItem {
  id: number;
  product: number;
  product_details: any;
  added_at: string;
}

interface WishlistContextType {
  wishlistItems: WishlistItem[];
  wishlistProductIds: Set<number>;
  getWishlistItemId: (productId: number) => number | null;
  addToWishlist: (productId: number) => Promise<void>;
  removeFromWishlist: (itemId: number) => Promise<void>;
  isWishlisted: (productId: number) => boolean;
  isLoading: boolean;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export function WishlistProvider({ children }: { children: ReactNode }) {
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchWishlist = useCallback(async () => {
    try {
      const res = await apiFetch("/api/wishlist/");
      if (res.ok) {
        const data = await res.json();
        setWishlistItems(data);
      }
    } catch (err) {
      // Silent fail on load
    }
  }, []);

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  const wishlistProductIds = new Set<number>(wishlistItems.map((i) => Number(i.product)));

  const getWishlistItemId = useCallback(
    (productId: number): number | null => {
      const item = wishlistItems.find((i) => Number(i.product) === productId);
      return item ? item.id : null;
    },
    [wishlistItems]
  );

  const isWishlisted = useCallback(
    (productId: number) => wishlistProductIds.has(Number(productId)),
    [wishlistItems]
  );

  const addToWishlist = useCallback(async (productId: number) => {
    setIsLoading(true);
    try {
      const res = await apiFetch("/api/wishlist/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product: productId }),
      });
      if (res.ok || res.status === 200) {
        const data = await res.json();
        // 201 = new item created, 200 = already in wishlist
        if (res.status === 201) {
          setWishlistItems((prev) => [...prev, data]);
        }
      }
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const removeFromWishlist = useCallback(async (itemId: number) => {
    setIsLoading(true);
    try {
      await apiFetch(`/api/wishlist/items/${itemId}/`, { method: "DELETE" });
      setWishlistItems((prev) => prev.filter((i) => i.id !== itemId));
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <WishlistContext.Provider
      value={{
        wishlistItems,
        wishlistProductIds,
        getWishlistItemId,
        addToWishlist,
        removeFromWishlist,
        isWishlisted,
        isLoading,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
}

export function useWishlist() {
  const context = useContext(WishlistContext);
  if (context === undefined) {
    throw new Error("useWishlist must be used within a WishlistProvider");
  }
  return context;
}
