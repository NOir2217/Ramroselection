import { useState, useEffect } from "react";
import { ProductCard } from "./ProductCard";
import { apiFetch } from "../utils/api";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface Props {
  title: string;
  endpoint: string;
}

export function ProductCarousel({ title, endpoint }: Props) {
  const [products, setProducts] = useState<any[]>([]);
  const [scrollIndex, setScrollIndex] = useState(0);

  useEffect(() => {
    apiFetch(endpoint)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setProducts(data);
      })
      .catch(() => {});
  }, [endpoint]);

  if (products.length === 0) return null;

  const visibleCount = 4; // desktop
  const maxIndex = Math.max(0, products.length - visibleCount);

  return (
    <section className="py-10">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">{title}</h2>
        <div className="flex gap-2">
          <button
            className="w-9 h-9 rounded-full border border-border flex items-center justify-center hover:bg-muted disabled:opacity-30 transition-colors"
            disabled={scrollIndex === 0}
            onClick={() => setScrollIndex(Math.max(0, scrollIndex - 1))}
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            className="w-9 h-9 rounded-full border border-border flex items-center justify-center hover:bg-muted disabled:opacity-30 transition-colors"
            disabled={scrollIndex >= maxIndex}
            onClick={() => setScrollIndex(Math.min(maxIndex, scrollIndex + 1))}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="overflow-hidden">
        <div
          className="flex gap-6 transition-transform duration-300"
          style={{ transform: `translateX(-${scrollIndex * (100 / visibleCount + 1.5)}%)` }}
        >
          {products.map((product) => (
            <div key={product.id} className="w-full min-w-[calc(25%-1.125rem)] sm:min-w-[calc(33.333%-1rem)] md:min-w-[calc(25%-1.125rem)]">
              <ProductCard product={product} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
