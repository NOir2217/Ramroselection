import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { ShoppingCart, Mail } from "lucide-react";
import { Button } from "../components/ui/button";

interface AbandonedItem {
  productName: string;
  quantity: number;
  unitPrice: number;
  size: string | null;
  color: string | null;
  shade: string | null;
}

interface AbandonedCart {
  id: string;
  customerEmail: string | null;
  customerName: string | null;
  itemCount: number;
  cartTotal: number;
  lastUpdated: string;
  items: AbandonedItem[];
}

export function AbandonedCartsPanel() {
  const [carts, setCarts] = useState<AbandonedCart[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(3);
  const [expandedCart, setExpandedCart] = useState<string | null>(null);

  const fetchCarts = () => {
    setLoading(true);
    apiFetch(`/api/orders/admin/abandoned-carts/?days=${days}`)
      .then((res) => res.json())
      .then((data) => { setCarts(data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchCarts(); }, [days]);

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <ShoppingCart className="h-7 w-7" />
          Abandoned Carts
        </h1>
        <div className="flex items-center gap-3">
          <label className="text-sm text-muted-foreground">Inactive for (days):</label>
          <Input
            type="number"
            className="w-20"
            min={1}
            max={90}
            value={days}
            onChange={(e) => setDays(Number(e.target.value) || 3)}
          />
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : carts.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No abandoned carts found for the selected period.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Customer</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Items</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Last Updated</TableHead>
                <TableHead>Details</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {carts.map((cart) => (
                <>
                  <TableRow key={cart.id} className="cursor-pointer" onClick={() => setExpandedCart(expandedCart === cart.id ? null : cart.id)}>
                    <TableCell className="font-medium">{cart.customerName || <span className="text-muted-foreground italic">Guest</span>}</TableCell>
                    <TableCell>{cart.customerEmail ? (
                      <a href={`mailto:${cart.customerEmail}`} className="text-primary hover:underline flex items-center gap-1">
                        <Mail className="h-3 w-3" /> {cart.customerEmail}
                      </a>
                    ) : <span className="text-muted-foreground">—</span>}</TableCell>
                    <TableCell><Badge variant="secondary">{cart.itemCount}</Badge></TableCell>
                    <TableCell className="font-mono">${cart.cartTotal.toFixed(2)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{formatDate(cart.lastUpdated)}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        {expandedCart === cart.id ? "Hide" : "View"}
                      </Button>
                    </TableCell>
                  </TableRow>
                  {expandedCart === cart.id && (
                    <TableRow key={`${cart.id}-items`}>
                      <TableCell colSpan={6} className="bg-muted/30 p-4">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-muted-foreground border-b">
                              <th className="text-left pb-2">Product</th>
                              <th className="text-left pb-2">Variants</th>
                              <th className="text-right pb-2">Qty</th>
                              <th className="text-right pb-2">Price</th>
                              <th className="text-right pb-2">Line Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {cart.items.map((item, idx) => {
                              const variants = [item.size, item.color, item.shade].filter(Boolean).join(" / ");
                              return (
                                <tr key={idx} className="border-b last:border-0">
                                  <td className="py-2">{item.productName}</td>
                                  <td className="py-2 text-muted-foreground">{variants || "—"}</td>
                                  <td className="py-2 text-right">{item.quantity}</td>
                                  <td className="py-2 text-right">${item.unitPrice.toFixed(2)}</td>
                                  <td className="py-2 text-right font-medium">${(item.quantity * item.unitPrice).toFixed(2)}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </TableCell>
                    </TableRow>
                  )}
                </>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}