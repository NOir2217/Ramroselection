import { useCompare } from "../context/CompareContext";
import { Link, useNavigate } from "react-router";
import { Button } from "./ui/button";
import { X, CheckSquare } from "lucide-react";

export function CompareBar() {
  const { compareList, removeFromCompare, clearCompare } = useCompare();
  const navigate = useNavigate();

  if (compareList.length === 0) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border shadow-2xl p-4 z-50 transform transition-transform duration-300">
      <div className="container mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4 w-full overflow-x-auto pb-2 sm:pb-0">
          <div className="flex-shrink-0 flex items-center gap-2 mr-4 hidden md:flex">
            <CheckSquare className="h-5 w-5 text-primary" />
            <span className="font-medium">Compare ({compareList.length}/3)</span>
          </div>
          
          <div className="flex gap-4">
            {compareList.map((item) => (
              <div key={item.id} className="relative flex items-center gap-2 bg-muted rounded p-1 pr-3 w-48 flex-shrink-0">
                <button 
                  onClick={() => removeFromCompare(item.id)}
                  className="absolute -top-2 -right-2 bg-destructive text-white rounded-full p-0.5 hover:scale-110 transition-transform"
                >
                  <X className="h-3 w-3" />
                </button>
                <div className="w-10 h-10 bg-white rounded overflow-hidden">
                  <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                </div>
                <span className="text-sm font-medium truncate">{item.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto flex-shrink-0">
          <Button variant="ghost" onClick={clearCompare} className="hidden sm:inline-flex">Clear All</Button>
          <Button 
            className="w-full sm:w-auto"
            disabled={compareList.length < 2}
            onClick={() => navigate('/compare')}
          >
            {compareList.length < 2 ? 'Select 1 more' : 'Compare Now'}
          </Button>
        </div>
      </div>
    </div>
  );
}
