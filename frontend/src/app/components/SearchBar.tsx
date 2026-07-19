import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Input } from "./ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { Link, useNavigate } from "react-router";
import { apiFetch } from "../utils/api";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  // Debounce the search query
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Fetch results when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      apiFetch(`/api/products/search/?q=${debouncedQuery}`)
        .then(res => res.json())
        .then(data => {
          setResults(data);
          setOpen(true);
        })
        .catch(() => setResults([]));
    } else {
      setResults([]);
      setOpen(false);
    }
  }, [debouncedQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setOpen(false);
      navigate(`/?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <form onSubmit={handleSearchSubmit} className="relative w-full max-w-sm flex-1 mx-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => { if (results.length > 0) setOpen(true); }}
            placeholder="Search products..."
            className="pl-10 bg-input-background"
          />
        </form>
      </PopoverTrigger>
      <PopoverContent
        className="w-[var(--radix-popover-trigger-width)] p-0 mt-1"
        align="start"
        onOpenAutoFocus={(e) => e.preventDefault()} // Prevent stealing focus back
      >
        <div className="flex flex-col max-h-80 overflow-y-auto">
          {results.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">No results found.</div>
          ) : (
            <>
              {results.map((product) => (
                <Link
                  key={product.id}
                  to={`/product/${product.slug}`}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-3 p-3 hover:bg-muted transition-colors border-b last:border-0"
                >
                  <img
                    src={product.image || "https://placehold.co/50"}
                    alt={product.name}
                    className="w-12 h-12 object-cover rounded-sm"
                  />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium truncate">{product.name}</h4>
                    <p className="text-xs text-muted-foreground">{product.category}</p>
                  </div>
                  <span className="text-sm font-semibold whitespace-nowrap">NRS {product.price}</span>
                </Link>
              ))}
              <div className="p-2 border-t bg-muted/30">
                <Button
                  variant="ghost"
                  className="w-full text-sm text-primary"
                  onClick={() => {
                    setOpen(false);
                    navigate(`/?q=${encodeURIComponent(query.trim())}`);
                  }}
                >
                  See all results for "{query}"
                </Button>
              </div>
            </>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Needed because we use Button in SearchBar
import { Button } from "./ui/button";
