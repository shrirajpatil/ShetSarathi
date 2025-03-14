from django.db import models
from category.models import Category
from app.models import Account
from django.urls import reverse
from django.db.models import Avg, Count
from django.template.defaultfilters import slugify

from helper import unique_product_slug_generator
from django.db.models.signals import pre_save




# models.py
class Product(models.Model):
    farmerID = models.IntegerField()
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    quantity = models.IntegerField()
    description = models.TextField(max_length=2000, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/photos', default="default.png")
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=100)  # Required for state filtering
    # Optional additional fields
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Bulk fields
    is_bulk_eligible = models.BooleanField(default=False, help_text="Available for bulk orders?")
    bulk_threshold = models.IntegerField(null=True, blank=True, help_text="Minimum quantity for bulk pricing")
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Bulk price per unit")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_date',)

    def avarageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(avarage=Avg('rating'))
        avg = 0
        if reviews['avarage'] is not None:
            avg = float(reviews['avarage'])
        return avg


    def countReview(self):
         reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
         count = 0
         if reviews['count'] is not None:
             count = int(reviews['count'])
         return count
       

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
        
    def __str__(self):
        return self.product_name


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_product_slug_generator(instance)
pre_save.connect(product_pre_save_receiver, sender=Product)


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject
     

class ProductGalary(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image =  models.ImageField(upload_to='store/product')
  
    class Meta:
        verbose_name = 'ProductGalary'
        verbose_name_plural = 'Product Galary'
    def __str__(self):
        return self.product.product_name
    

class Recommendation(models.Model):
    recommendation_order = models.IntegerField()
    score = models.FloatField()

    def __str__(self):
        return f"Recommendation {self.id}"