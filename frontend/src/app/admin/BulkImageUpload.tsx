import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "sonner";
import { Upload, X, GripVertical, ImageIcon } from "lucide-react";

interface Product {
  id: number;
  name: string;
  sku: string;
  imageCount: number;
}

interface UploadedImage {
  id: number;
  image_url: string;
  image_type: string;
  display_order: number;
}

export function BulkImageUpload() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [loadingImages, setLoadingImages] = useState(false);

  const [newImages, setNewImages] = useState([
    { image_url: "", image_type: "angle", display_order: 0 },
  ]);

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

  const selectProduct = async (product: Product) => {
    setSelectedProduct(product);
    setLoadingImages(true);

    try {
      const res = await apiFetch(`/api/products/${product.slug}/`);
      const data = await res.json();
      setImages(data.images || []);
    } catch {
      toast.error("Failed to load images");
    } finally {
      setLoadingImages(false);
    }
  };

  const addImageRow = () => {
    setNewImages([
      ...newImages,
      { image_url: "", image_type: "angle", display_order: newImages.length },
    ]);
  };

  const removeImageRow = (idx: number) => {
    setNewImages(newImages.filter((_, i) => i !== idx));
  };

  const updateImageRow = (idx: number, field: string, value: string | number) => {
    const updated = [...newImages];
    (updated[idx] as any)[field] = value;
    setNewImages(updated);
  };

  const uploadImages = async () => {
    if (!selectedProduct) return;

    const validImages = newImages.filter((img) => img.image_url.trim());
    if (validImages.length === 0) {
      toast.error("Add at least one image URL");
      return;
    }

    try {
      const res = await apiFetch(`/api/products/admin/${selectedProduct.id}/images/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ images: validImages }),
      });

      if (res.ok) {
        toast.success(`${validImages.length} image(s) added`);
        const updatedRes = await apiFetch(`/api/products/${selectedProduct.slug}/`);
        const data = await updatedRes.json();
        setImages(data.images || []);
        setNewImages([{ image_url: "", image_type: "angle", display_order: 0 }]);
      } else {
        toast.error("Failed to upload images");
      }
    } catch {
      toast.error("Network error");
    }
  };

  const deleteImage = async (imageId: number) => {
    if (!selectedProduct) return;
    if (!confirm("Delete this image?")) return;

    try {
      const res = await apiFetch(`/api/products/admin/${selectedProduct.id}/images/`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: imageId }),
      });

      if (res.ok) {
        setImages((prev) => prev.filter((img) => img.id !== imageId));
        toast.success("Image deleted");
      }
    } catch {
      toast.error("Network error");
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold flex items-center gap-2">
        <ImageIcon className="h-7 w-7" />
        Bulk Image Upload
      </h1>

      <div className="flex items-center gap-3">
        <Input
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-4">
          <h2 className="font-semibold mb-3">Select Product</h2>
          {loading ? (
            <div className="p-4 text-center text-muted-foreground">Loading...</div>
          ) : (
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {products.map((p) => (
                <button
                  key={p.id}
                  onClick={() => selectProduct(p)}
                  className={`w-full text-left p-3 rounded border transition-colors ${
                    selectedProduct?.id === p.id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{p.name}</p>
                      <p className="text-xs text-muted-foreground">{p.sku}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">{p.imageCount} imgs</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>

        <Card className="p-4">
          {selectedProduct ? (
            <div className="space-y-4">
              <h2 className="font-semibold">
                Images: {selectedProduct.name}
              </h2>

              {loadingImages ? (
                <div className="p-4 text-center text-muted-foreground">Loading...</div>
              ) : (
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {images.map((img) => (
                    <div key={img.id} className="flex items-center gap-3 p-2 border rounded">
                      <img src={img.image_url} alt="" className="w-12 h-12 object-cover rounded" />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs truncate">{img.image_url}</p>
                        <p className="text-xs text-muted-foreground">{img.image_type} • Order: {img.display_order}</p>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => deleteImage(img.id)}>
                        <X className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  ))}
                  {images.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center">No images yet.</p>
                  )}
                </div>
              )}

              <div className="border-t pt-4">
                <h3 className="text-sm font-medium mb-2">Add New Images</h3>
                <div className="space-y-2">
                  {newImages.map((img, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <Input
                        placeholder="Image URL"
                        value={img.image_url}
                        onChange={(e) => updateImageRow(idx, "image_url", e.target.value)}
                        className="flex-1"
                      />
                      <Select value={img.image_type} onValueChange={(val) => updateImageRow(idx, "image_type", val)}>
                        <SelectTrigger className="w-[130px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="primary">Primary</SelectItem>
                          <SelectItem value="angle">Angle</SelectItem>
                          <SelectItem value="swatch">Swatch</SelectItem>
                          <SelectItem value="on_model">On Model</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input
                        type="number"
                        placeholder="#"
                        value={img.display_order}
                        onChange={(e) => updateImageRow(idx, "display_order", Number(e.target.value))}
                        className="w-16"
                      />
                      {newImages.length > 1 && (
                        <Button variant="ghost" size="sm" onClick={() => removeImageRow(idx)}>
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-3">
                  <Button variant="outline" size="sm" onClick={addImageRow}>
                    + Add Row
                  </Button>
                  <Button size="sm" onClick={uploadImages}>
                    <Upload className="h-4 w-4 mr-1" />
                    Upload
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              Select a product to manage images
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
