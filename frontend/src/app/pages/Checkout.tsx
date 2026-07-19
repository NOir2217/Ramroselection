import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { Link, useNavigate } from "react-router";
import { apiFetch } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function Checkout() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<any>(null);
  const { user } = useAuth();
  const { fetchCart } = useCart();
  const [continueAsGuest, setContinueAsGuest] = useState(false);
  const navigate = useNavigate();
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      email: '',
      firstName: '',
      lastName: '',
      address: '',
      city: '',
      postalCode: '',
      phone: ''
    }
  });

  // Pre-fill email for logged-in users
  useEffect(() => {
    if (user) {
      reset({
        email: user.email || '',
        firstName: '',
        lastName: '',
        address: '',
        city: '',
        postalCode: '',
        phone: ''
      });
    }
  }, [user, reset]);

  const onSubmit = (data: any) => {
    setLoading(true);
    apiFetch("/api/checkout/", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Ensure cart_token cookie is transmitted
      body: JSON.stringify({ email: data.email, shipping_info: data })
    })
    .then(res => res.json().then(json => ({ ok: res.ok, data: json })))
    .then(({ ok, data }) => {
      setLoading(false);
      if (ok) {
        setSuccess(data);
        toast.success("Order placed successfully!");
        // Refresh cart in context since it's cleared now
        fetchCart();
      } else {
        toast.error(data.detail || "Failed to place order.");
      }
    })
    .catch(() => {
      setLoading(false);
      toast.error("Network error");
    });
  };

  if (success) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl font-bold mb-4 text-green-600">Thank you for your order!</h1>
        <p className="text-lg text-muted-foreground mb-8">Your order number is <strong className="text-foreground">{success.order_number}</strong>.</p>
        <Link to="/">
          <Button size="lg">Continue Shopping</Button>
        </Link>
      </div>
    );
  }

  // If user is guest and hasn't chosen to continue as guest, show the options screen
  if (!user && !continueAsGuest) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 min-h-[calc(100vh-10rem)] flex items-center justify-center">
        <div className="w-full space-y-6 bg-card p-8 border rounded-xl shadow-sm text-center">
          <h1 className="text-2xl font-bold">Checkout</h1>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Please sign in to proceed with your saved addresses and loyalty rewards, or checkout as a guest.
          </p>
          <div className="flex flex-col gap-3 pt-2">
            <Button 
              className="w-full h-11 text-base font-medium"
              onClick={() => navigate("/login", { state: { from: { pathname: "/checkout" } } })}
            >
              Sign In to Account
            </Button>
            <Button 
              variant="outline" 
              className="w-full h-11 text-base font-medium"
              onClick={() => navigate("/register", { state: { from: { pathname: "/checkout" } } })}
            >
              Create a New Account
            </Button>
            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-border"></div>
              <span className="flex-shrink mx-4 text-xs text-muted-foreground uppercase">or</span>
              <div className="flex-grow border-t border-border"></div>
            </div>
            <Button 
              variant="secondary" 
              className="w-full h-11 text-base font-medium"
              onClick={() => setContinueAsGuest(true)}
            >
              Continue as Guest
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 md:py-12">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      
      <form onSubmit={handleSubmit(onSubmit)} className="grid md:grid-cols-3 gap-10">
        <div className="md:col-span-2 space-y-8">
          {/* Contact Info */}
          <section>
            <h2 className="text-xl font-semibold mb-4">Contact Information</h2>
            <div>
              <Input 
                placeholder="Email Address" 
                type="email"
                {...register("email", { required: "Email is required" })}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && <span className="text-red-500 text-sm mt-1">{errors.email.message}</span>}
            </div>
          </section>

          {/* Shipping Info */}
          <section>
            <h2 className="text-xl font-semibold mb-4">Shipping Address</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Input placeholder="First Name" {...register("firstName", { required: "First name is required" })} />
                {errors.firstName && <span className="text-red-500 text-sm mt-1">{errors.firstName.message}</span>}
              </div>
              <div>
                <Input placeholder="Last Name" {...register("lastName", { required: "Last name is required" })} />
                {errors.lastName && <span className="text-red-500 text-sm mt-1">{errors.lastName.message}</span>}
              </div>
              <div className="col-span-2">
                <Input placeholder="Address" {...register("address", { required: "Address is required" })} />
                {errors.address && <span className="text-red-500 text-sm mt-1">{errors.address.message}</span>}
              </div>
              <div>
                <Input placeholder="City" {...register("city", { required: "City is required" })} />
                {errors.city && <span className="text-red-500 text-sm mt-1">{errors.city.message}</span>}
              </div>
              <div>
                <Input placeholder="Postal Code" {...register("postalCode")} />
              </div>
              <div className="col-span-2">
                <Input placeholder="Phone Number" {...register("phone", { required: "Phone number is required" })} />
                {errors.phone && <span className="text-red-500 text-sm mt-1">{errors.phone.message}</span>}
              </div>
            </div>
          </section>
        </div>

        {/* Order Summary & Payment Placeholder */}
        <div className="bg-gray-50 p-6 rounded-xl h-fit border border-gray-100">
          <h2 className="text-xl font-semibold mb-4">Payment</h2>
          <p className="text-sm text-muted-foreground mb-6">Payment integration will be added in Phase 4. For now, you will pay Cash on Delivery.</p>
          
          <Button type="submit" className="w-full h-12 text-lg" disabled={loading}>
            {loading ? "Processing..." : "Place Order (COD)"}
          </Button>
        </div>
      </form>
    </div>
  );
}
