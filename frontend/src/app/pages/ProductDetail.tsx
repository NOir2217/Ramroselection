import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";
import { Star } from "lucide-react";
import { apiFetch } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import { ProductCarousel } from "../components/ProductCarousel";

export function ProductDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const [product, setProduct] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Selection State
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [activeImage, setActiveImage] = useState<string>("");

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/products/${slug}/`)
      .then((res) => res.json())
      .then((data) => {
        setProduct(data);
        setActiveImage(data.image);
        if (data.variants && data.variants.length > 0) {
          setSelectedSize(data.variants[0].size);
          setSelectedColor(data.variants[0].color);
        }
        setLoading(false);

        // Fire-and-forget: record this product view
        apiFetch("/api/recently-viewed/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product: data.id })
        }).catch(() => {}); // silently ignore errors
      });
  }, [slug]);

  // Auto-preselect user's default size if logged in
  useEffect(() => {
    if (product && user) {
      apiFetch("/api/auth/preferences/")
        .then(res => res.ok ? res.json() : null)
        .then(prefs => {
          if (prefs?.default_size) {
            const availSizes = product.variants?.map((v: any) => v.size).filter(Boolean);
            if (availSizes?.includes(prefs.default_size)) {
              setSelectedSize(prefs.default_size);
            }
          }
        })
        .catch(() => {});
    }
  }, [product, user]);

  if (loading) return <div className="p-20 text-center text-lg">Loading...</div>;
  if (!product) return <div className="p-20 text-center text-lg text-destructive">Product not found.</div>;

  // Derive unique sizes and colors for UI
  const availableSizes = Array.from(new Set(product.variants?.map((v: any) => v.size).filter(Boolean)));
  const availableColors = Array.from(new Set(product.variants?.map((v: any) => v.color).filter(Boolean)));
  
  // Find currently selected variant based on UI selection
  const selectedVariant = product.variants?.find(
    (v: any) => v.size === selectedSize && v.color === selectedColor
  ) || product.variants?.[0];

  const handleAddToCart = () => {
    if (!selectedVariant) {
      toast.error("Please select all options");
      return;
    }
    fetch('http://127.0.0.1:8000/api/cart/items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ variantId: selectedVariant.id, quantity })
    })
    .then((res) => {
      if(res.ok) {
        toast.success("Added to cart");
      } else {
        toast.error("Failed to add to cart");
      }
    });
  };

  const images = [product.image, ...(product.images?.map((i: any) => i.image_url) || [])];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 md:py-12">
      <div className="grid md:grid-cols-2 gap-10">
        
        {/* Image Gallery */}
        <div className="flex flex-col-reverse md:flex-row gap-4">
          <div className="flex md:flex-col gap-2 overflow-x-auto md:w-24 shrink-0">
            {images.map((img: string, idx: number) => (
              <img 
                key={idx} 
                src={img} 
                alt="Thumbnail" 
                className={`w-20 h-24 md:w-full md:h-32 object-cover rounded-md cursor-pointer border-2 transition-all ${activeImage === img ? 'border-primary' : 'border-transparent opacity-70 hover:opacity-100'}`}
                onClick={() => setActiveImage(img)}
              />
            ))}
          </div>
          <div className="flex-1 bg-gray-50 rounded-xl overflow-hidden aspect-[3/4] md:aspect-auto">
            <img src={activeImage} alt={product.name} className="w-full h-full object-cover" />
          </div>
        </div>

        {/* Product Info */}
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
          <div className="flex items-center gap-4 mb-4">
            <span className="text-2xl font-bold">NRS {selectedVariant ? product.price + selectedVariant.extra_price : product.price}</span>
            <div className="flex items-center text-sm text-muted-foreground">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 mr-1" />
              {product.rating} ({product.reviewCount} reviews)
            </div>
          </div>

          <p className="text-muted-foreground mb-6 line-clamp-3">{product.description}</p>

          {/* Selectors */}
          {availableColors.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Color: <span className="font-normal text-muted-foreground">{selectedColor}</span></h3>
              <div className="flex flex-wrap gap-2">
                {availableColors.map((color: any) => (
                  <button 
                    key={color}
                    className={`px-4 py-2 border rounded-md transition-all ${selectedColor === color ? 'border-primary bg-primary/5 font-medium' : 'hover:border-gray-400'}`}
                    onClick={() => setSelectedColor(color)}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>
          )}

          {availableSizes.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Size: <span className="font-normal text-muted-foreground">{selectedSize}</span></h3>
              <div className="flex flex-wrap gap-2">
                {availableSizes.map((size: any) => (
                  <button 
                    key={size}
                    className={`px-4 py-2 border rounded-md transition-all ${selectedSize === size ? 'border-primary bg-primary/5 font-medium' : 'hover:border-gray-400'}`}
                    onClick={() => setSelectedSize(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity & Add to Cart */}
          <div className="flex items-center gap-4 mt-auto pt-6">
            <div className="flex items-center border rounded-md h-12">
              <button className="px-4 text-muted-foreground hover:text-foreground" onClick={() => setQuantity(Math.max(1, quantity - 1))}>-</button>
              <span className="w-8 text-center font-medium">{quantity}</span>
              <button className="px-4 text-muted-foreground hover:text-foreground" onClick={() => setQuantity(quantity + 1)}>+</button>
            </div>
            <Button className="flex-1 h-12 text-lg" onClick={handleAddToCart}>
              Add to Cart
            </Button>
          </div>
          {selectedVariant && selectedVariant.stock_quantity <= 5 && (
            <p className="text-red-500 text-sm mt-2">Only {selectedVariant.stock_quantity} left in stock!</p>
          )}
        </div>
      </div>

      {/* Details Tabs */}
      <div className="mt-16">
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="w-full justify-start border-b rounded-none h-auto p-0 bg-transparent gap-8">
            <TabsTrigger value="details" className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:shadow-none rounded-none py-3">Details</TabsTrigger>
            <TabsTrigger value="materials" className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:shadow-none rounded-none py-3">Materials</TabsTrigger>
            {product.sizeGuide && <TabsTrigger value="size" className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:shadow-none rounded-none py-3">Size Guide</TabsTrigger>}
            <TabsTrigger value="reviews" className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:shadow-none rounded-none py-3">Reviews</TabsTrigger>
          </TabsList>
          <TabsContent value="details" className="py-6 text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {product.description}
          </TabsContent>
          <TabsContent value="materials" className="py-6 text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {product.material_or_ingredients || 'Information not provided.'}
          </TabsContent>
          {product.sizeGuide && (
            <TabsContent value="size" className="py-6">
              <p className="mb-4">Size guide for {product.sizeGuide.brand || product.sizeGuide.categoryName}</p>
              {/* Size guide table would go here based on product.sizeGuide.chart_data */}
            </TabsContent>
          )}
          <TabsContent value="reviews" className="py-6">
            {product.reviews && product.reviews.length > 0 ? (
              <div className="space-y-6">
                {product.reviews.map((rev: any) => (
                  <div key={rev.id} className="border-b pb-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{rev.customerName}</span>
                        <div className="flex">
                          {[...Array(5)].map((_, i) => (
                            <Star key={i} className={`w-3 h-3 ${i < rev.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
                          ))}
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">{new Date(rev.created_at).toLocaleDateString()}</span>
                    </div>
                    <h4 className="font-medium mb-1">{rev.title}</h4>
                    <p className="text-muted-foreground text-sm">{rev.body}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No reviews yet.</p>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Recommendations */}
      {slug && (
        <ProductCarousel
          title="You May Also Like"
          endpoint={`/api/products/${slug}/recommendations/`}
        />
      )}

      {/* Recently Viewed */}
      <ProductCarousel
        title="Recently Viewed"
        endpoint="/api/recently-viewed/"
      />
    </div>
  );
}
