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
import { WishlistPage } from "./pages/WishlistPage";
import { OrderTracking } from "./pages/OrderTracking";
import { ComparePage } from "./pages/ComparePage";
import { CompareBar } from "./components/CompareBar";

export default function App() {
  return (
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
          <Route path="/admin/*" element={<AdminLayout />} />
        </Routes>
      </main>
      <CompareBar />
      <Footer />
      <Toaster />
    </div>
  );
}