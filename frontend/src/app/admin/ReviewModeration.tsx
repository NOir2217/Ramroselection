import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { CheckCircle, XCircle, Star, MessageSquare } from "lucide-react";

interface PendingReview {
  id: number;
  productName: string;
  customerName: string;
  rating: number;
  title: string;
  body: string;
  photoUrls: string[];
  createdAt: string;
}

export function ReviewModeration() {
  const [reviews, setReviews] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReviews = () => {
    setLoading(true);
    apiFetch("/api/products/admin/reviews/")
      .then((res) => res.json())
      .then((data) => {
        setReviews(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const moderateReview = async (reviewId: number, approved: boolean) => {
    try {
      const res = await apiFetch(`/api/products/admin/reviews/${reviewId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isApproved: approved }),
      });

      if (res.ok) {
        toast.success(approved ? "Review approved" : "Review rejected");
        setReviews((prev) => prev.filter((r) => r.id !== reviewId));
      }
    } catch {
      toast.error("Failed to moderate review");
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold flex items-center gap-2">
        <MessageSquare className="h-7 w-7" />
        Review Moderation
        {reviews.length > 0 && (
          <Badge variant="secondary" className="ml-2">{reviews.length} pending</Badge>
        )}
      </h1>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="p-4 animate-pulse">
              <div className="h-4 bg-muted rounded w-32 mb-2" />
              <div className="h-3 bg-muted rounded w-48 mb-4" />
              <div className="h-16 bg-muted rounded" />
            </Card>
          ))}
        </div>
      ) : reviews.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          No pending reviews to moderate.
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reviews.map((review) => (
            <Card key={review.id} className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-medium text-sm">{review.productName}</p>
                  <p className="text-xs text-muted-foreground">
                    by {review.customerName} • {new Date(review.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-3 w-3 ${i < review.rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`}
                    />
                  ))}
                </div>
              </div>

              <h4 className="font-medium text-sm mb-1">{review.title}</h4>
              <p className="text-sm text-muted-foreground mb-3">{review.body}</p>

              {review.photoUrls && review.photoUrls.length > 0 && (
                <div className="flex gap-2 mb-3">
                  {review.photoUrls.map((url, i) => (
                    <img key={i} src={url} alt="" className="w-12 h-12 object-cover rounded border" />
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                  onClick={() => moderateReview(review.id, true)}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Approve
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="text-red-600 border-red-200 hover:bg-red-50"
                  onClick={() => moderateReview(review.id, false)}
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Reject
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
