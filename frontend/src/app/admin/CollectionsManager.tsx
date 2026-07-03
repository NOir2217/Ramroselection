import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Checkbox } from "../components/ui/checkbox";
import { toast } from "sonner";
import { Plus, Edit, Trash2, LayoutGrid, Search } from "lucide-react";

interface Collection {
  id: number;
  name: string;
  slug: string;
  description: string;
  bannerImageUrl: string | null;
  isActive: boolean;
  displayOrder: number;
  productCount: number;
}

interface Product {
  id: number;
  name: string;
  selected?: boolean;
}

export function CollectionsManager() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(false);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCollection, setEditingCollection] = useState<Collection | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    slug: "",
    description: "",
    bannerImageUrl: "",
    isActive: true,
    displayOrder: 0,
  });

  const fetchCollections = () => {
    setLoading(true);
    apiFetch(`/api/products/admin/collections/?search=${search}`)
      .then((res) => res.json())
      .then((data) => {
        setCollections(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchCollections();
  }, [search]);

  const fetchProducts = async () => {
    if (products.length > 0) return;
    setProductsLoading(true);
    try {
      const res = await apiFetch("/api/products/admin/list/?search=");
      const data = await res.json();
      setProducts(data.map((p: any) => ({ ...p, selected: false })));
    } catch {
      toast.error("Failed to load products");
    } finally {
      setProductsLoading(false);
    }
  };

  const openCreate = () => {
    setEditingCollection(null);
    setFormData({ name: "", slug: "", description: "", bannerImageUrl: "", isActive: true, displayOrder: 0 });
    setDialogOpen(true);
  };

  const openEdit = async (c: Collection) => {
    setEditingCollection(c);
    setFormData({
      name: c.name,
      slug: c.slug,
      description: c.description,
      bannerImageUrl: c.bannerImageUrl || "",
      isActive: c.isActive,
      displayOrder: c.displayOrder,
    });
    setDialogOpen(true);
  };

  const saveCollection = async () => {
    const selectedProductIds = products.filter((p) => p.selected).map((p) => p.id);
    const payload = { ...formData, products: selectedProductIds };

    try {
      let res: Response;
      if (editingCollection) {
        res = await apiFetch(`/api/products/admin/collections/${editingCollection.id}/`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        res = await apiFetch("/api/products/admin/collections/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (res.ok) {
        toast.success(editingCollection ? "Collection updated" : "Collection created");
        setDialogOpen(false);
        fetchCollections();
      } else {
        toast.error("Failed to save collection");
      }
    } catch {
      toast.error("Network error");
    }
  };

  const deleteCollection = async (id: number) => {
    if (!confirm("Delete this collection?")) return;
    try {
      const res = await apiFetch(`/api/products/admin/collections/${id}/`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Collection deleted");
        setCollections((prev) => prev.filter((c) => c.id !== id));
      }
    } catch {
      toast.error("Failed to delete");
    }
  };

  const toggleProductSelection = (productId: number) => {
    setProducts((prev) => prev.map((p) => p.id === productId ? { ...p, selected: !p.selected } : p));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <LayoutGrid className="h-7 w-7" />
          Collections
        </h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => { openCreate(); fetchProducts(); }}>
              <Plus className="h-4 w-4 mr-2" />
              New Collection
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingCollection ? "Edit Collection" : "New Collection"}</DialogTitle>
            </DialogHeader>

            <div className="space-y-4 py-2">
              <div>
                <label className="text-sm font-medium mb-1 block">Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Collection name"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Slug</label>
                <Input
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  placeholder="URL slug"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Description</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Banner Image URL</label>
                <Input
                  value={formData.bannerImageUrl}
                  onChange={(e) => setFormData({ ...formData, bannerImageUrl: e.target.value })}
                  placeholder="https://..."
                />
              </div>
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium">Active</label>
                <Checkbox
                  checked={formData.isActive}
                  onCheckedChange={(checked) => setFormData({ ...formData, isActive: !!checked })}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Display Order</label>
                <Input
                  type="number"
                  value={formData.displayOrder}
                  onChange={(e) => setFormData({ ...formData, displayOrder: Number(e.target.value) })}
                />
              </div>

              <div className="pt-2">
                <h3 className="font-semibold mb-2">Products in Collection</h3>
                <div className="border rounded-md max-h-48 overflow-y-auto">
                  {productsLoading ? (
                    <div className="p-4 text-center text-muted-foreground">Loading products...</div>
                  ) : (
                    products.map((p) => (
                      <label key={p.id} className="flex items-center gap-2 px-3 py-2 hover:bg-muted/50 cursor-pointer">
                        <Checkbox
                          checked={p.selected}
                          onCheckedChange={() => toggleProductSelection(p.id)}
                        />
                        <span className="text-sm">{p.name}</span>
                      </label>
                    ))
                  )}
                </div>
              </div>

              <Button className="w-full" onClick={saveCollection}>
                {editingCollection ? "Update Collection" : "Create Collection"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search collections..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : collections.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No collections found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Collection</TableHead>
                <TableHead>Slug</TableHead>
                <TableHead>Products</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Order</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {collections.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.name}</TableCell>
                  <TableCell className="font-mono text-xs">{c.slug}</TableCell>
                  <TableCell>{c.productCount}</TableCell>
                  <TableCell>
                    <Badge variant={c.isActive ? "default" : "secondary"}>
                      {c.isActive ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>{c.displayOrder}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => { openEdit(c); fetchProducts(); }}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => deleteCollection(c.id)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}