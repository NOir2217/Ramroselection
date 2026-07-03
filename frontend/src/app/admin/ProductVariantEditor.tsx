import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { toast } from "sonner";
import { Plus, Trash2, Package } from "lucide-react";

interface Product {
  id: number;
  name: string;
  sku: string;
  slug: string;
  productType: string;
  variantCount: number;
  imageCount: number;
  lowStockVariants: number;
}

interface Variant {
  id: number;
  size: string | null;
  color: string | null;
  color_hex: string | null;
  shade: string | null;
  shade_hex: string | null;
  volume: string | null;
  stock_quantity: number;
  low_stock_threshold: number;
  batch_number: string | null;
  expiration_date: string | null;
  extra_price: number;
  sku_suffix: string;
}

export function ProductVariantEditor() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [loadingVariants, setLoadingVariants] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  const [newVariant, setNewVariant] = useState({
    size: "",
    color: "",
    color_hex: "",
    shade: "",
    shade_hex: "",
    volume: "",
    stock_quantity: 10,
    low_stock_threshold: 5,
    batch_number: "",
    expiration_date: "",
    extra_price: 0,
    sku_suffix: "",
  });

  const fetchProducts = () => {
    setLoading(true);
    apiFetch(`/api/products/admin/list/?search=${search}`)
      .then((res) => res.json())
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts();
  }, [search]);

  const openVariants = async (product: Product) => {
    setSelectedProduct(product);
    setLoadingVariants(true);
    setDialogOpen(true);

    try {
      const res = await apiFetch(`/api/products/admin/${product.id}/variants/`);
      const data = await res.json();
      setVariants(data);
    } catch {
      toast.error("Failed to load variants");
    } finally {
      setLoadingVariants(false);
    }
  };

  const addVariant = async () => {
    if (!selectedProduct) return;

    const payload: any = {
      stock_quantity: newVariant.stock_quantity,
      low_stock_threshold: newVariant.low_stock_threshold,
      extra_price: newVariant.extra_price,
      sku_suffix: newVariant.sku_suffix || "DEF",
    };

    if (newVariant.size) payload.size = newVariant.size;
    if (newVariant.color) payload.color = newVariant.color;
    if (newVariant.color_hex) payload.color_hex = newVariant.color_hex;
    if (newVariant.shade) payload.shade = newVariant.shade;
    if (newVariant.shade_hex) payload.shade_hex = newVariant.shade_hex;
    if (newVariant.volume) payload.volume = newVariant.volume;
    if (newVariant.batch_number) payload.batch_number = newVariant.batch_number;
    if (newVariant.expiration_date) payload.expiration_date = newVariant.expiration_date;

    try {
      const res = await apiFetch(`/api/products/admin/${selectedProduct.id}/variants/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        toast.success("Variant added");
        const updatedRes = await apiFetch(`/api/products/admin/${selectedProduct.id}/variants/`);
        setVariants(await updatedRes.json());
        setNewVariant({
          size: "", color: "", color_hex: "", shade: "", shade_hex: "",
          volume: "", stock_quantity: 10, low_stock_threshold: 5,
          batch_number: "", expiration_date: "", extra_price: 0, sku_suffix: "",
        });
      } else {
        toast.error("Failed to add variant");
      }
    } catch {
      toast.error("Network error");
    }
  };

  const deleteVariant = async (variantId: number) => {
    if (!selectedProduct) return;
    if (!confirm("Delete this variant?")) return;

    try {
      const res = await apiFetch(`/api/products/admin/${selectedProduct.id}/variants/`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: variantId }),
      });

      if (res.ok) {
        toast.success("Variant deleted");
        setVariants((prev) => prev.filter((v) => v.id !== variantId));
      }
    } catch {
      toast.error("Network error");
    }
  };

  const getVariantLabel = (v: Variant) => {
    return [v.size, v.color, v.shade, v.volume].filter(Boolean).join(" / ") || "Default";
  };

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold flex items-center gap-2">
        <Package className="h-7 w-7" />
        Variant Management
      </h1>

      <div className="flex items-center gap-3">
        <Input
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : products.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No products found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-center">Variants</TableHead>
                <TableHead className="text-center">Low Stock</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell className="font-mono text-xs">{p.sku}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{p.productType}</Badge>
                  </TableCell>
                  <TableCell className="text-center">{p.variantCount}</TableCell>
                  <TableCell className="text-center">
                    {p.lowStockVariants > 0 ? (
                      <Badge className="bg-red-100 text-red-800">{p.lowStockVariants}</Badge>
                    ) : (
                      <span className="text-muted-foreground">0</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" onClick={() => openVariants(p)}>
                      Manage Variants
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Variants: {selectedProduct?.name}
            </DialogTitle>
          </DialogHeader>

          {loadingVariants ? (
            <div className="p-4 text-center text-muted-foreground">Loading variants...</div>
          ) : (
            <div className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Variant</TableHead>
                    <TableHead className="text-center">Stock</TableHead>
                    <TableHead>Batch</TableHead>
                    <TableHead>Expires</TableHead>
                    <TableHead>Extra Price</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {variants.map((v) => (
                    <TableRow key={v.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {v.color_hex && (
                            <div className="w-4 h-4 rounded-full border" style={{ backgroundColor: v.color_hex }} />
                          )}
                          {v.shade_hex && (
                            <div className="w-4 h-4 rounded-full border" style={{ backgroundColor: v.shade_hex }} />
                          )}
                          {getVariantLabel(v)}
                        </div>
                      </TableCell>
                      <TableCell className="text-center">{v.stock_quantity}</TableCell>
                      <TableCell className="text-xs">{v.batch_number || "-"}</TableCell>
                      <TableCell className="text-xs">{v.expiration_date || "-"}</TableCell>
                      <TableCell>NRS {v.extra_price}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" onClick={() => deleteVariant(v.id)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {variants.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        No variants yet. Add one below.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              <Card className="p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add New Variant
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {selectedProduct?.productType === "clothing" ? (
                    <>
                      <Input placeholder="Size (S/M/L)" value={newVariant.size} onChange={(e) => setNewVariant({ ...newVariant, size: e.target.value })} />
                      <Input placeholder="Color" value={newVariant.color} onChange={(e) => setNewVariant({ ...newVariant, color: e.target.value })} />
                      <Input placeholder="Color Hex (#fff)" value={newVariant.color_hex} onChange={(e) => setNewVariant({ ...newVariant, color_hex: e.target.value })} />
                      <Input placeholder="SKU Suffix" value={newVariant.sku_suffix} onChange={(e) => setNewVariant({ ...newVariant, sku_suffix: e.target.value })} />
                    </>
                  ) : (
                    <>
                      <Input placeholder="Shade" value={newVariant.shade} onChange={(e) => setNewVariant({ ...newVariant, shade: e.target.value })} />
                      <Input placeholder="Shade Hex (#fff)" value={newVariant.shade_hex} onChange={(e) => setNewVariant({ ...newVariant, shade_hex: e.target.value })} />
                      <Input placeholder="Volume (30ml)" value={newVariant.volume} onChange={(e) => setNewVariant({ ...newVariant, volume: e.target.value })} />
                      <Input placeholder="SKU Suffix" value={newVariant.sku_suffix} onChange={(e) => setNewVariant({ ...newVariant, sku_suffix: e.target.value })} />
                    </>
                  )}
                  <Input
                    type="number"
                    placeholder="Stock qty"
                    value={newVariant.stock_quantity}
                    onChange={(e) => setNewVariant({ ...newVariant, stock_quantity: Number(e.target.value) })}
                  />
                  <Input
                    type="number"
                    placeholder="Extra price"
                    value={newVariant.extra_price}
                    onChange={(e) => setNewVariant({ ...newVariant, extra_price: Number(e.target.value) })}
                  />
                  <Input placeholder="Batch #" value={newVariant.batch_number} onChange={(e) => setNewVariant({ ...newVariant, batch_number: e.target.value })} />
                  <Input type="date" placeholder="Expiration" value={newVariant.expiration_date} onChange={(e) => setNewVariant({ ...newVariant, expiration_date: e.target.value })} />
                </div>
                <Button className="mt-3" onClick={addVariant}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add Variant
                </Button>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
