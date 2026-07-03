import React, { createContext, useContext, useState, ReactNode } from 'react';
import { toast } from "sonner";

interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  slug?: string;
  // additional specs can be loaded on the compare page
}

interface CompareContextType {
  compareList: Product[];
  toggleCompare: (product: Product) => void;
  removeFromCompare: (id: string) => void;
  clearCompare: () => void;
  isCompared: (id: string) => boolean;
}

const CompareContext = createContext<CompareContextType | undefined>(undefined);

export function CompareProvider({ children }: { children: ReactNode }) {
  const [compareList, setCompareList] = useState<Product[]>([]);

  const toggleCompare = (product: Product) => {
    if (isCompared(product.id)) {
      setCompareList(prev => prev.filter(p => p.id !== product.id));
    } else {
      if (compareList.length >= 3) {
        toast.warning("You can only compare up to 3 items at a time.");
        return;
      }
      setCompareList(prev => [...prev, product]);
      toast.success(`${product.name} added to comparison`);
    }
  };

  const removeFromCompare = (id: string) => {
    setCompareList(prev => prev.filter(p => p.id !== id));
  };

  const clearCompare = () => {
    setCompareList([]);
  };

  const isCompared = (id: string) => {
    return compareList.some(p => p.id === id);
  };

  return (
    <CompareContext.Provider value={{ compareList, toggleCompare, removeFromCompare, clearCompare, isCompared }}>
      {children}
    </CompareContext.Provider>
  );
}

export function useCompare() {
  const context = useContext(CompareContext);
  if (context === undefined) {
    throw new Error("useCompare must be used within a CompareProvider");
  }
  return context;
}
