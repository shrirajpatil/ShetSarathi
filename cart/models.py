from django.db import models
from store.models import Product
from django.utils import timezone
from app.models import Account
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, unique=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
        

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE ,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)

    def sub_total(self):
        # Check for accepted negotiation request
        negotiation = NegotiationRequest.objects.filter(
            buyer=self.user,
            product=self.product,
            quantity=self.quantity,
            status='Accepted'
        ).first()
        if negotiation:
            # Use the total negotiated price for this quantity
            return negotiation.proposed_price
        # Fallback to bulk price or original price per unit
        price = self.product.bulk_price if (
            self.product.is_bulk_eligible and 
            self.quantity >= (self.product.bulk_threshold or float('inf')) and 
            self.product.bulk_price
        ) else self.product.price
        return price * self.quantity

    def __str__(self):
        return f'{self.product}'

class NegotiationRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='negotiation_requests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.product.product_name} - ${self.proposed_price}"
    
        
    