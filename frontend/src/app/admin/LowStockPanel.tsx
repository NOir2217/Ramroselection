import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { Link } from "react-router";

interface LowStockVariant {
  id: number;
  productName: string;
  productSlug: string;
  size: string | null;
  color: string | null;
  shade: string | null;
  volume: string | null;
  stockQuantity: number;
  lowStockThreshold: number;
  sku: string;
  isExpired: boolean;
}

export function LowStockPanel() {
  const [variants, setVariants] = useState<LowStockVariant[]>([]);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState(5);

  const fetchVariants = () => {
    setLoading(true);
    apiFetch(`/api/orders/admin/inventory/low-stock/?threshold=${threshold}`)
      .then((res) => res.json())
      .then((data) => {
        setVariants(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchVariants();
  }, [threshold]);

  const getVariantLabel = (v: LowStockVariant) => {
    const parts = [v.size, v.color, v.shade, v.volume].filter(Boolean);
    return parts.join(" / ") || "Default";
  };

  const getStockBadge = (qty: number) => {
    if (qty === 0) return <Badge variant="destructive">Out of Stock</Badge>;
    if (qty <= 2) return <Badge className="bg-red-100 text-red-800">{qty} left</Badge>;
    return <Badge className="bg-yellow-100 text-yellow-800">{qty} left</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <AlertTriangle className="h-7 w-7 text-orange-500" />
          Low Stock Alerts
        </h1>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Threshold:</span>
            <select
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="border rounded px-2 py-1 text-sm"
            >
              {[3, 5, 10, 15, 20].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <Button variant="outline" size="sm" onClick={fetchVariants}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : variants.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            All variants are above the threshold.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>Variant</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead className="text-center">Stock</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {variants.map((v) => (
                <TableRow key={v.id}>
                  <TableCell>
                    <Link to={`/product/${v.productSlug}`} className="hover:underline font-medium">
                      {v.productName}
                    </Link>
                  </TableCell>
                  <TableCell>{getVariantLabel(v)}</TableCell>
                  <TableCell className="font-mono text-xs">{v.sku}</TableCell>
                  <TableCell className="text-center font-semibold">{v.stockQuantity}</TableCell>
                  <TableCell>{getStockBadge(v.stockQuantity)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
