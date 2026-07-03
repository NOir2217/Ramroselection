import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "sonner";
import { Plus, Edit, Trash2, Percent } from "lucide-react";

interface DiscountRule {
  id: number;
  code: string | null;
  rule_type: string;
  config: Record<string, any>;
  active_from: string | null;
  active_to: string | null;
  is_active: boolean;
}

const RULE_TYPE_LABELS: Record<string, string> = {
  percent_off: "Percent Off",
  buy_x_get_y: "Buy X Get Y",
  bundle_fixed_price: "Bundle Fixed Price",
  free_gift: "Free Gift",
};

export function DiscountsManager() {
  const [rules, setRules] = useState<DiscountRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<DiscountRule | null>(null);
  const [formData, setFormData] = useState({
    code: "",
    rule_type: "percent_off",
    config: "{}",
    active_from: "",
    active_to: "",
    is_active: true,
  });

  const fetchRules = () => {
    setLoading(true);
    apiFetch("/api/orders/admin/discounts/")
      .then((res) => res.json())
      .then((data) => { setRules(data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchRules(); }, []);

  const openCreate = () => {
    setEditing(null);
    setFormData({ code: "", rule_type: "percent_off", config: "{}", active_from: "", active_to: "", is_active: true });
    setDialogOpen(true);
  };

  const openEdit = (r: DiscountRule) => {
    setEditing(r);
    setFormData({
      code: r.code || "",
      rule_type: r.rule_type,
      config: JSON.stringify(r.config, null, 2),
      active_from: r.active_from || "",
      active_to: r.active_to || "",
      is_active: r.is_active,
    });
    setDialogOpen(true);
  };

  const parseConfig = (raw: string): Record<string, any> => {
    try { return JSON.parse(raw); } catch { return {}; }
  };

  const save = async () => {
    const payload: any = {
      rule_type: formData.rule_type,
      config: parseConfig(formData.config),
      is_active: formData.is_active,
    };
    if (formData.code.trim()) payload.code = formData.code.trim();
    if (formData.active_from) payload.active_from = formData.active_from;
    if (formData.active_to) payload.active_to = formData.active_to;

    try {
      let res: Response;
      if (editing) {
        res = await apiFetch(`/api/orders/admin/discounts/${editing.id}/`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        res = await apiFetch("/api/orders/admin/discounts/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      if (res.ok) {
        toast.success(editing ? "Discount updated" : "Discount created");
        setDialogOpen(false);
        fetchRules();
      } else {
        const err = await res.json();
        toast.error(Object.values(err).flat().join(", "));
      }
    } catch {
      toast.error("Network error");
    }
  };

  const deleteRule = async (id: number) => {
    if (!confirm("Delete this discount rule?")) return;
    try {
      const res = await apiFetch(`/api/orders/admin/discounts/${id}/`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Rule deleted");
        setRules((prev) => prev.filter((r) => r.id !== id));
      }
    } catch {
      toast.error("Failed to delete");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Percent className="h-7 w-7" />
          Discount Rules
        </h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="h-4 w-4 mr-2" />
              New Discount
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editing ? "Edit Discount Rule" : "New Discount Rule"}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div>
                <label className="text-sm font-medium mb-1 block">Rule Type</label>
                <Select value={formData.rule_type} onValueChange={(v) => setFormData({ ...formData, rule_type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(RULE_TYPE_LABELS).map(([k, v]) => (
                      <SelectItem key={k} value={k}>{v}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Code (optional — auto-generated if blank)</label>
                <Input value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} placeholder="e.g. SAVE20" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Config (JSON)</label>
                <Textarea value={formData.config} onChange={(e) => setFormData({ ...formData, config: e.target.value })} rows={5} placeholder='{"percent": 10}' />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium mb-1 block">Active From</label>
                  <Input type="datetime-local" value={formData.active_from} onChange={(e) => setFormData({ ...formData, active_from: e.target.value })} />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Active To</label>
                  <Input type="datetime-local" value={formData.active_to} onChange={(e) => setFormData({ ...formData, active_to: e.target.value })} />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is-active" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />
                <label htmlFor="is-active" className="text-sm">Active</label>
              </div>
              <Button className="w-full" onClick={save}>{editing ? "Update" : "Create"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : rules.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No discount rules found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Config</TableHead>
                <TableHead>Active</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rules.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-mono font-medium">{r.code || <span className="text-muted-foreground italic">auto</span>}</TableCell>
                  <TableCell><Badge variant="outline">{RULE_TYPE_LABELS[r.rule_type] || r.rule_type}</Badge></TableCell>
                  <TableCell className="font-mono text-xs max-w-[200px] truncate">{JSON.stringify(r.config)}</TableCell>
                  <TableCell><Badge variant={r.is_active ? "default" : "secondary"}>{r.is_active ? "Active" : "Inactive"}</Badge></TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openEdit(r)}><Edit className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="sm" onClick={() => deleteRule(r.id)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
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