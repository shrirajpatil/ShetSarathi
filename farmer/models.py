from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='products/photos')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    category = models.CharField(max_length=100, default="General")
    quantity = models.IntegerField(default=0)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    # New bulk fields
    is_bulk_eligible = models.BooleanField(default=False, help_text="Available for bulk orders?")
    bulk_threshold = models.IntegerField(null=True, blank=True, help_text="Minimum quantity for bulk pricing")
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Bulk price per unit")

    def __str__(self):
        return self.name

class Recommendation(models.Model):
    recommendation_order = models.IntegerField()
    score = models.FloatField()

    def __str__(self):
        return f"Recommendation {self.id}"