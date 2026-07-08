import { Heart, Star, ShoppingCart } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { useState } from "react";
import { Link } from "react-router";
import { toast } from "sonner";
import { useCompare } from "../context/CompareContext";
import { useWishlist } from "../context/WishlistContext";

interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviewCount: number;
  image: string;
  isNew?: boolean;
  isSale?: boolean;
  salePercentage?: number;
  slug?: string;
}

interface ProductCardProps {
  product: Product;
  /** If set, clicking "Add to Cart" calls this directly (e.g. when the parent knows the variant). */
  onAddToCart?: (productId: string) => void;
  /** @deprecated — remove state is now managed by WishlistContext */
  onWishlistToggle?: (productId: string) => void;
  /** @deprecated — wishlist state now comes from WishlistContext */
  initiallyWishlisted?: boolean;
}

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const { toggleCompare, isCompared } = useCompare();
  const { isWishlisted, addToWishlist, removeFromWishlist, getWishlistItemId } = useWishlist();

  const wishlisted = isWishlisted(Number(product.id));

  const handleWishlistClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      if (!wishlisted) {
        await addToWishlist(Number(product.id));
        toast.success("Added to wishlist");
      } else {
        const itemId = getWishlistItemId(Number(product.id));
        if (itemId !== null) {
          await removeFromWishlist(itemId);
          toast.info("Removed from wishlist");
        }
      }
    } catch (err) {
      toast.error("Failed to update wishlist");
    }
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onAddToCart) {
      onAddToCart(product.id);
    } else {
      // No variant context available from catalogue view — navigate to product detail for variant selection
      window.location.href = `/product/${product.slug || product.id}`;
    }
  };
  
  const handleCompareChange = (_e: React.ChangeEvent<HTMLInputElement>) => {
    toggleCompare(product);
  };

  const productUrl = `/product/${product.slug || product.id}`;
  const compared = isCompared(product.id);

  return (
    <Card 
      className={`group relative overflow-hidden transition-all duration-300 hover:shadow-lg ${isHovered ? 'scale-[1.02]' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardContent className="p-0">
        {/* Image Container */}
        <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
          <Link to={productUrl} className="absolute inset-0 z-0">
            <ImageWithFallback
              src={product.image}
              alt={product.name}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          </Link>
          
          {/* Compare Checkbox */}
          <div className={`absolute top-2 left-2 z-10 transition-opacity duration-200 ${compared || isHovered ? 'opacity-100' : 'opacity-0'}`}>
            <label className="flex items-center gap-2 bg-background/90 p-1.5 rounded text-xs cursor-pointer hover:bg-background border border-border shadow-sm">
              <input type="checkbox" className="w-3.5 h-3.5 accent-primary" checked={compared} onChange={handleCompareChange} />
              Compare
            </label>
          </div>

          {/* Badges */}
          <div className="absolute top-10 left-2 flex flex-col gap-1 z-10 pointer-events-none">
            {product.isNew && (
              <Badge variant="secondary" className="bg-green-500 text-white">
                NEW
              </Badge>
            )}
            {product.isSale && (
              <Badge variant="destructive">
                -{product.salePercentage}%
              </Badge>
            )}
          </div>

          {/* Wishlist Button */}
          <Button
            variant="ghost"
            size="sm"
            className={`absolute top-2 right-2 h-8 w-8 p-0 transition-all duration-200 z-10 ${
              wishlisted 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-background/80 hover:bg-background'
            }`}
            onClick={handleWishlistClick}
          >
            <Heart 
              className={`h-4 w-4 ${wishlisted ? 'fill-current' : ''}`} 
            />
          </Button>

          {/* Add to Cart Button - Shows on hover */}
          <div className={`absolute bottom-2 left-2 right-2 transition-all duration-300 z-10 ${
            isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
          }`}>
            <Button 
              onClick={handleAddToCart}
              className="w-full"
              size="sm"
            >
              <ShoppingCart className="h-4 w-4 mr-2" />
              Add to Cart
            </Button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-4">
          <Link to={productUrl} className="hover:underline">
            <h3 className="font-medium mb-2 line-clamp-2">{product.name}</h3>
          </Link>

          
          {/* Rating */}
          <div className="flex items-center gap-1 mb-2">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-3 w-3 ${
                    i < Math.floor(product.rating)
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-muted-foreground">
              ({product.reviewCount})
            </span>
          </div>

          {/* Price */}
          <div className="flex items-center gap-2">
            <span className="font-bold">NRS {product.price}</span>
            {product.originalPrice && (
              <span className="text-sm text-muted-foreground line-through">
                NRS {product.originalPrice}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}