import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { AlertTriangle, RefreshCw, Skull } from "lucide-react";
import { Link } from "react-router";

interface ExpiringVariant {
  id: number;
  productName: string;
  productSlug: string;
  shade: string | null;
  volume: string | null;
  batchNumber: string | null;
  expirationDate: string;
  stockQuantity: number;
  isExpired: boolean;
}

export function ExpiringProductsPanel() {
  const [variants, setVariants] = useState<ExpiringVariant[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchVariants = () => {
    setLoading(true);
    apiFetch(`/api/orders/admin/inventory/expiring/?days=${days}`)
      .then((res) => res.json())
      .then((data) => {
        setVariants(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchVariants();
  }, [days]);

  const getDaysUntilExpiry = (dateStr: string) => {
    const now = new Date();
    const exp = new Date(dateStr);
    const diffMs = exp.getTime() - now.getTime();
    return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  };

  const getExpiryBadge = (dateStr: string, isExpired: boolean) => {
    if (isExpired) return <Badge variant="destructive">Expired</Badge>;
    const daysLeft = getDaysUntilExpiry(dateStr);
    if (daysLeft <= 7) return <Badge className="bg-red-100 text-red-800">{daysLeft}d left</Badge>;
    if (daysLeft <= 14) return <Badge className="bg-orange-100 text-orange-800">{daysLeft}d left</Badge>;
    return <Badge className="bg-yellow-100 text-yellow-800">{daysLeft}d left</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Skull className="h-7 w-7 text-red-500" />
          Expiring Products
        </h1>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Within:</span>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="border rounded px-2 py-1 text-sm"
            >
              {[7, 14, 30, 60, 90].map((n) => (
                <option key={n} value={n}>{n} days</option>
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
            No products expiring within {days} days.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>Variant</TableHead>
                <TableHead>Batch</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead>Stock</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {variants.map((v) => (
                <TableRow key={v.id} className={v.isExpired ? "bg-red-50" : ""}>
                  <TableCell>
                    <Link to={`/product/${v.productSlug}`} className="hover:underline font-medium">
                      {v.productName}
                    </Link>
                  </TableCell>
                  <TableCell>{[v.shade, v.volume].filter(Boolean).join(" / ") || "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{v.batchNumber || "-"}</TableCell>
                  <TableCell className="text-sm">{v.expirationDate}</TableCell>
                  <TableCell className="text-center">{v.stockQuantity}</TableCell>
                  <TableCell>{getExpiryBadge(v.expirationDate, v.isExpired)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
