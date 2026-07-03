import { useCompare } from "../context/CompareContext";
import { Link, Navigate } from "react-router";
import { ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "../components/ui/button";

export function ComparePage() {
  const { compareList, removeFromCompare } = useCompare();

  if (compareList.length < 2) {
    return <Navigate to="/" replace />;
  }

  // Define the rows we want to show for comparison
  const rows = [
    { label: "Price", render: (p: any) => `NRS ${p.price}` },
    { label: "Rating", render: (p: any) => `${p.rating}★ (${p.reviewCount} reviews)` },
    { label: "Availability", render: (p: any) => p.isNew ? "New Arrival" : p.isSale ? "On Sale" : "In Stock" },
  ];

  return (
    <div className="container mx-auto px-4 py-12 min-h-[calc(100vh-10rem)]">
      <div className="mb-8 flex items-center justify-between">
        <Link to="/" className="flex items-center text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Shopping
        </Link>
        <h1 className="text-3xl font-bold">Compare Products</h1>
      </div>

      <div className="overflow-x-auto pb-8">
        <table className="w-full min-w-[800px] border-collapse bg-card border border-border rounded-lg overflow-hidden">
          <thead>
            <tr>
              <th className="p-4 border-b border-r border-border bg-muted/50 w-1/4 text-left">
                <span className="font-semibold text-lg">Product Features</span>
              </th>
              {compareList.map(product => (
                <th key={product.id} className="p-6 border-b border-r border-border text-center w-1/4 last:border-r-0">
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 bg-white rounded overflow-hidden mb-4 shadow-sm border border-border">
                      <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
                    </div>
                    <h3 className="font-bold text-lg mb-2 line-clamp-2 min-h-[3.5rem]">{product.name}</h3>
                    <Button 
                      variant="destructive" 
                      size="sm" 
                      onClick={() => removeFromCompare(product.id)}
                      className="mt-2"
                    >
                      <Trash2 className="h-4 w-4 mr-2" /> Remove
                    </Button>
                  </div>
                </th>
              ))}
              {/* Fill empty columns if less than 3 items */}
              {Array.from({ length: 3 - compareList.length }).map((_, i) => (
                <th key={`empty-${i}`} className="p-6 border-b border-r border-border bg-muted/20 text-center w-1/4 last:border-r-0">
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <div className="w-32 h-32 border-2 border-dashed border-muted-foreground/30 rounded flex items-center justify-center mb-4">
                      +
                    </div>
                    <p>Add a product to compare</p>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-muted/10 transition-colors">
                <td className="p-4 border-b border-r border-border font-medium bg-muted/20">
                  {row.label}
                </td>
                {compareList.map(product => (
                  <td key={product.id} className="p-4 border-b border-r border-border text-center last:border-r-0">
                    {row.render(product)}
                  </td>
                ))}
                {Array.from({ length: 3 - compareList.length }).map((_, i) => (
                  <td key={`empty-cell-${idx}-${i}`} className="p-4 border-b border-r border-border text-center bg-muted/10 last:border-r-0" />
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
