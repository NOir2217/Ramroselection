import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import {
  TrendingUp, DollarSign, Package, Users, BarChart3,
  PieChart, ShoppingCart, ArrowUpDown,
} from "lucide-react";

interface DataPoint {
  label: string;
  value: number;
}

interface TopProduct {
  productName: string;
  productId: number;
  totalSold: number;
  totalRevenue: number;
}

interface CategoryRevenue {
  category: string;
  revenue: number;
}

interface GrowthPoint {
  label: string;
  newCustomers: number;
  totalCustomers: number;
}

interface OrderVolumePoint {
  label: string;
  orderCount: number;
  revenue: number;
}

interface AOVPoint {
  label: string;
  avgOrderValue: number;
}

interface AnalyticsData {
  revenueOverTime: DataPoint[];
  topProducts: TopProduct[];
  revenueByCategory: CategoryRevenue[];
  customerGrowth: GrowthPoint[];
  orderVolume: OrderVolumePoint[];
  averageOrderValue: number;
  aovOverTime: AOVPoint[];
  period: string;
}

const MAX_BARS = 20;

function MiniBarChart({ data, color = "bg-primary", height = 100 }: { data: DataPoint[]; color?: string; height?: number }) {
  if (!data || data.length === 0) return <div className="text-muted-foreground text-sm py-4 text-center">No data</div>;
  const sliced = data.slice(-MAX_BARS);
  const maxVal = Math.max(...sliced.map((d) => d.value), 1);
  return (
    <div className="flex items-end gap-[2px]" style={{ height }}>
      {sliced.map((d, i) => (
        <div
          key={i}
          className={`${color} rounded-t flex-1 min-w-[4px] transition-all duration-300`}
          style={{ height: `${(d.value / maxVal) * 100}%` }}
          title={`${d.label}: ${d.value}`}
        />
      ))}
    </div>
  );
}

function HorizontalBarChart({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm w-32 truncate text-right">{label}</span>
      <div className="flex-1 bg-muted rounded-full h-5 overflow-hidden">
        <div className={`${color} h-full rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-mono w-24 text-right">{value.toLocaleString()}</span>
    </div>
  );
}

export function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState("monthly");

  const fetchData = () => {
    setLoading(true);
    apiFetch(`/api/orders/admin/analytics/?period=${period}`)
      .then((res) => res.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [period]);

  const periods = [
    { key: "daily", label: "30 Days" },
    { key: "weekly", label: "90 Days" },
    { key: "monthly", label: "12 Months" },
    { key: "yearly", label: "5 Years" },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="p-6 animate-pulse"><div className="h-48 bg-muted rounded" /></Card>
          ))}
        </div>
      </div>
    );
  }

  const barColor = "bg-primary";
  const catColors = ["bg-blue-500", "bg-green-500", "bg-purple-500", "bg-orange-500", "bg-pink-500", "bg-teal-500", "bg-red-500", "bg-yellow-500"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <BarChart3 className="h-7 w-7" />
          Analytics & Reports
        </h1>
        <div className="flex gap-2">
          {periods.map((p) => (
            <Button key={p.key} variant={period === p.key ? "default" : "outline"} size="sm" onClick={() => setPeriod(p.key)}>
              {p.label}
            </Button>
          ))}
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Avg Order Value</span>
            <DollarSign className="h-4 w-4 text-green-600" />
          </div>
          <p className="text-2xl font-bold">NPR {data?.averageOrderValue.toLocaleString() ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Top Product Revenue</span>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </div>
          <p className="text-2xl font-bold">NPR {(data?.topProducts?.[0]?.totalRevenue ?? 0).toLocaleString()}</p>
          <p className="text-xs text-muted-foreground truncate">{data?.topProducts?.[0]?.productName ?? "—"}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">Total Orders</span>
            <ShoppingCart className="h-4 w-4 text-purple-600" />
          </div>
          <p className="text-2xl font-bold">{data?.orderVolume?.reduce((s, v) => s + v.orderCount, 0) ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground">New Customers</span>
            <Users className="h-4 w-4 text-orange-600" />
          </div>
          <p className="text-2xl font-bold">{data?.customerGrowth?.reduce((s, v) => s + v.newCustomers, 0) ?? 0}</p>
        </Card>
      </div>

      {/* Revenue Over Time */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Revenue Over Time
        </h2>
        <MiniBarChart data={data?.revenueOverTime ?? []} color={barColor} height={160} />
        <div className="flex justify-between text-xs text-muted-foreground mt-2">
          <span>{data?.revenueOverTime?.[0]?.label ?? ""}</span>
          <span>{data?.revenueOverTime?.slice(-1)?.[0]?.label ?? ""}</span>
        </div>
      </Card>

      {/* Two-column: Top Products + Category Revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Package className="h-5 w-5" />
            Top 10 Products
          </h2>
          {data?.topProducts && data.topProducts.length > 0 ? (
            <div className="space-y-3">
              {data.topProducts.map((p, i) => (
                <HorizontalBarChart
                  key={p.productId}
                  label={`${i + 1}. ${p.productName}`}
                  value={p.totalRevenue}
                  max={data.topProducts[0].totalRevenue}
                  color={catColors[i % catColors.length]}
                />
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No product revenue data.</p>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Revenue by Category
          </h2>
          {data?.revenueByCategory && data.revenueByCategory.length > 0 ? (
            <div className="space-y-3">
              {data.revenueByCategory.map((c, i) => (
                <HorizontalBarChart
                  key={c.category}
                  label={c.category}
                  value={c.revenue}
                  max={data.revenueByCategory[0].revenue}
                  color={catColors[i % catColors.length]}
                />
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No category revenue data.</p>
          )}
        </Card>
      </div>

      {/* Two-column: Order Volume + AOV Over Time */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Order Volume
          </h2>
          <MiniBarChart
            data={(data?.orderVolume ?? []).map((v) => ({ label: v.label, value: v.orderCount }))}
            color="bg-purple-500"
            height={140}
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-2">
            <span>{data?.orderVolume?.[0]?.label ?? ""}</span>
            <span>{data?.orderVolume?.slice(-1)?.[0]?.label ?? ""}</span>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Average Order Value Over Time
          </h2>
          <MiniBarChart
            data={(data?.aovOverTime ?? []).map((v) => ({ label: v.label, value: v.avgOrderValue }))}
            color="bg-green-500"
            height={140}
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-2">
            <span>{data?.aovOverTime?.[0]?.label ?? ""}</span>
            <span>{data?.aovOverTime?.slice(-1)?.[0]?.label ?? ""}</span>
          </div>
        </Card>
      </div>

      {/* Customer Growth */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Users className="h-5 w-5" />
          Customer Growth
        </h2>
        {data?.customerGrowth && data.customerGrowth.length > 0 ? (
          <div className="space-y-3">
            {data.customerGrowth.map((g, i) => (
              <div key={i} className="flex items-center gap-4 text-sm">
                <span className="font-mono w-20">{g.label}</span>
                <div className="flex-1 flex items-center gap-1">
                  <div className="bg-blue-500 rounded h-4" style={{ width: `${Math.max(2, (g.newCustomers / Math.max(...data.customerGrowth.map((x) => x.newCustomers), 1)) * 100)}%` }} />
                  <span className="text-muted-foreground">+{g.newCustomers}</span>
                </div>
                <Badge variant="secondary" className="w-24 justify-center">Total: {g.totalCustomers}</Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No customer data for this period.</p>
        )}
      </Card>
    </div>
  );
}