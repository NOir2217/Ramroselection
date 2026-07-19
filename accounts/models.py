from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customerprofile')
    email = models.EmailField() # Not unique, to allow guests multiple checkouts with the same email if needed
    default_size = models.CharField(max_length=50, null=True, blank=True)
    skin_type = models.CharField(max_length=50, null=True, blank=True)
    is_vip = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"Profile: {self.user.username} ({self.email})"
        return f"Guest Profile: {self.email}"

class Address(models.Model):
    profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f"{self.full_name} - {self.street}, {self.city}"
