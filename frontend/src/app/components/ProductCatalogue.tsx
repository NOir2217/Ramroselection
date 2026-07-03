import { useState, useMemo, useEffect } from "react";
import { ProductCard } from "./ProductCard";
import { FilterPanel } from "./FilterPanel";
import { SortDropdown, SortOption } from "./SortDropdown";
import { Button } from "./ui/button";
import { Filter, Grid, List } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { toast } from "sonner";
import { useSearchParams } from "react-router";

interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviewCount: number;
  image: string;
  category: string;
  slug: string;
  isNew?: boolean;
  isSale?: boolean;
  salePercentage?: number;
}

export function ProductCatalogue() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  const [sortBy, setSortBy] = useState<SortOption>("relevance");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  useEffect(() => {
    let active = true;
    setLoading(true);
    
    // Construct API query string from URL search params
    const query = new URLSearchParams(searchParams.toString());
    
    fetch(`/api/products/?${query.toString()}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch products");
        }
        return res.json();
      })
      .then((data) => {
        if (active) {
          setProducts(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (active) {
          console.error(err);
          setError(err.message || "An error occurred while loading products.");
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [searchParams]);

  // Frontend Sort & basic filters
  const filteredAndSortedProducts = useMemo(() => {
    let result = [...products];

    // Read local min rating and price from searchParams if they exist, or just rely on backend.
    // For now, we will sort on frontend as requested previously.
    switch (sortBy) {
      case "price-low-high":
        result.sort((a, b) => a.price - b.price);
        break;
      case "price-high-low":
        result.sort((a, b) => b.price - a.price);
        break;
      case "rating":
        result.sort((a, b) => b.rating - a.rating);
        break;
      case "name":
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case "newest":
        result.sort((a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0));
        break;
      default:
        break;
    }

    return result;
  }, [products, sortBy]);

  const handleAddToCart = (productId: string) => {
    toast.success("Product added to cart!");
  };

  const handleWishlistToggle = (productId: string) => {
    toast.success("Wishlist updated!");
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p className="text-lg text-muted-foreground animate-pulse">Loading products catalogue...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p className="text-lg text-red-500 font-medium">{error}</p>
        <Button onClick={() => { setLoading(true); setError(null); }} className="mt-4">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex gap-6">
        {/* Desktop Filter Panel */}
        <div className="hidden lg:block flex-shrink-0">
          <FilterPanel />
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {/* Controls Bar */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <div className="flex items-center gap-4">
              <h1>Products ({filteredAndSortedProducts.length})</h1>
              
              {/* Mobile Filter Button */}
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="lg:hidden">
                    <Filter className="h-4 w-4 mr-2" />
                    Filters
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-80 p-0">
                  <div className="p-4">
                    <FilterPanel isMobile={true} />
                  </div>
                </SheetContent>
              </Sheet>
            </div>

            <div className="flex items-center gap-4">
              {/* View Mode Toggle */}
              <div className="flex items-center border rounded-md">
                <Button
                  variant={viewMode === "grid" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                  className="rounded-r-none"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                  className="rounded-l-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>

              {/* Sort Dropdown */}
              <SortDropdown value={sortBy} onChange={setSortBy} />
            </div>
          </div>

          {/* Products Grid */}
          {filteredAndSortedProducts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No products found matching your filters.</p>
              <Button variant="outline" onClick={() => setFilters({
                categories: [],
                priceRange: [0, 50000],
                minRating: 0,
              })} className="mt-4">
                Clear Filters
              </Button>
            </div>
          ) : (
            <div className={
              viewMode === "grid" 
                ? "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6"
                : "space-y-4"
            }>
              {filteredAndSortedProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={handleAddToCart}
                  onWishlistToggle={handleWishlistToggle}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}