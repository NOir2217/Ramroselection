import { Routes, Route } from "react-router";
import { Header } from "./components/Header";
import { ProductCatalogue } from "./components/ProductCatalogue";
import { Footer } from "./components/Footer";
import { Toaster } from "./components/ui/sonner";
import { ProductDetail } from "./pages/ProductDetail";
import { Checkout } from "./pages/Checkout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { MyAccount } from "./pages/MyAccount";
import { AdminLayout } from "./admin/AdminLayout";
import { AdminDashboard } from "./admin/AdminDashboard";
import { OrdersKanban } from "./admin/OrdersKanban";
import { LowStockPanel } from "./admin/LowStockPanel";
import { ExpiringProductsPanel } from "./admin/ExpiringProductsPanel";
import { ProductVariantEditor } from "./admin/ProductVariantEditor";
import { BulkImageUpload } from "./admin/BulkImageUpload";
import { ReviewModeration } from "./admin/ReviewModeration";
import { CollectionsManager } from "./admin/CollectionsManager";
import { DiscountsManager } from "./admin/DiscountsManager";
import { AbandonedCartsPanel } from "./admin/AbandonedCartsPanel";
import { AnalyticsDashboard } from "./admin/AnalyticsDashboard";
import { WishlistPage } from "./pages/WishlistPage";
import { OrderTracking } from "./pages/OrderTracking";
import { ComparePage } from "./pages/ComparePage";
import { CompareBar } from "./components/CompareBar";
import { CartProvider } from "./context/CartContext";
import { WishlistProvider } from "./context/WishlistContext";

export default function App() {
  return (
    <CartProvider>
      <WishlistProvider>
        <div className="min-h-screen bg-background">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<ProductCatalogue />} />
              <Route path="/product/:slug" element={<ProductDetail />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/wishlist" element={<WishlistPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/account" element={<MyAccount />} />
              <Route path="/orders/:orderNumber" element={<OrderTracking />} />
              <Route path="/compare" element={<ComparePage />} />

              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminDashboard />} />
                <Route path="orders" element={<OrdersKanban />} />
                <Route path="low-stock" element={<LowStockPanel />} />
                <Route path="expiring" element={<ExpiringProductsPanel />} />
                <Route path="variants" element={<ProductVariantEditor />} />
                <Route path="images" element={<BulkImageUpload />} />
                <Route path="reviews" element={<ReviewModeration />} />
                <Route path="collections" element={<CollectionsManager />} />
                <Route path="discounts" element={<DiscountsManager />} />
                <Route path="analytics" element={<AnalyticsDashboard />} />
                <Route path="abandoned-carts" element={<AbandonedCartsPanel />} />
              </Route>
            </Routes>
          </main>
          <CompareBar />
          <Footer />
          <Toaster />
        </div>
      </WishlistProvider>
    </CartProvider>
  );
}
