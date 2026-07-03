import { Search, ShoppingCart, User, Menu } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { useState } from "react";
import { CartDrawer } from "./CartDrawer";
import { Link } from "react-router";
import { SearchBar } from "./SearchBar";

interface HeaderProps {
  cartItemsCount?: number;
  onMenuToggle?: () => void;
}

export function Header({ cartItemsCount = 0, onMenuToggle }: HeaderProps) {
  const [isCartOpen, setIsCartOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={onMenuToggle}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
                <span className="text-primary-foreground font-bold">R</span>
              </div>
              <span className="font-bold text-lg hidden sm:block">Ramro Selection</span>
            </Link>
          </div>

          {/* Navigation - Hidden on mobile */}
          <nav className="hidden md:flex items-center gap-6">
            <Link to="/" className="hover:text-primary transition-colors font-medium">Home</Link>
            <Link to="/?category=clothing" className="hover:text-primary transition-colors font-medium">Clothing</Link>
            <Link to="/?category=cosmetics" className="hover:text-primary transition-colors font-medium">Cosmetics</Link>
          </nav>

          {/* Search Bar - Hidden on small screens */}
          <div className="hidden sm:flex flex-1 justify-center max-w-lg">
            <SearchBar />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="sm:hidden">
              <Search className="h-5 w-5" />
            </Button>
            <Link to="/wishlist">
              <Button variant="ghost" size="sm">
                <Heart className="h-5 w-5" />
              </Button>
            </Link>
            <Button variant="ghost" size="sm" className="relative" onClick={() => setIsCartOpen(true)}>
              <ShoppingCart className="h-5 w-5" />
              {cartItemsCount > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs rounded-full"
                >
                  {cartItemsCount}
                </Badge>
              )}
            </Button>
            <Link to="/account">
              <Button variant="ghost" size="sm">
                <User className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>
      
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </>
  );
}