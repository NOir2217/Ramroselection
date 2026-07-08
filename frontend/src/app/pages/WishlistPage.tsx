import { useWishlist } from "../context/WishlistContext";
import { ProductCard } from "../components/ProductCard";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { HeartCrack } from "lucide-react";

export function WishlistPage() {
  const { wishlistItems, removeFromWishlist, isLoading } = useWishlist();

  const handleRemove = async (itemId: number) => {
    try {
      await removeFromWishlist(itemId);
      toast.success("Item removed");
    } catch (err) {
      toast.error("Failed to remove item");
    }
  };

  if (isLoading && wishlistItems.length === 0) {
    return <div className="container mx-auto px-4 py-16 text-center">Loading wishlist...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-12 min-h-[calc(100vh-10rem)]">
      <h1 className="text-3xl font-bold mb-8">My Wishlist</h1>
      
      {wishlistItems.length === 0 ? (
        <div className="text-center py-20 bg-muted/20 rounded-lg">
          <HeartCrack className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h2 className="text-xl font-medium mb-2">Your wishlist is empty</h2>
          <p className="text-muted-foreground mb-6">Save items you love to find them later.</p>
          <Button onClick={() => window.location.href = "/"}>Continue Shopping</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {wishlistItems.map((item) => (
            <div key={item.id} className="relative">
              <ProductCard 
                product={item.product_details} 
              />
              <Button 
                variant="destructive" 
                size="sm"
                className="absolute -top-2 -right-2 z-20 rounded-full w-8 h-8 p-0"
                onClick={() => handleRemove(item.id)}
                title="Remove from wishlist"
              >
                &times;
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
