from django.db import models

class WishlistItem(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='wishlist_items')
    session_key = models.CharField(max_length=255, null=True, blank=True) # for guest wishlist tracking
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('customer', 'product'), ('session_key', 'product')]

    def __str__(self):
        identifier = self.customer or f"session:{self.session_key}"
        return f"Wishlist: {identifier} -> {self.product.name}"

class RecentlyViewed(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='recently_viewed')
    session_key = models.CharField(max_length=255, null=True, blank=True) # for guest recently viewed
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='recently_viewed')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'recently viewed'

    def __str__(self):
        identifier = self.customer or f"session:{self.session_key}"
        return f"Viewed: {identifier} -> {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1–5 stars
    title = models.CharField(max_length=255)
    body = models.TextField()
    photo_urls = models.JSONField(default=list, blank=True) # list of photo URLs
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer or 'guest'} on {self.product.name} ({self.rating}★)"
