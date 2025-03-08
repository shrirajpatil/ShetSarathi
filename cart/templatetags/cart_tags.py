from django import template
from cart.models import NegotiationRequest

register = template.Library()

@register.filter
def lookup(cart_item, attr):
    if attr == "negotiation":
        return NegotiationRequest.objects.filter(
            buyer=cart_item.user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            status='Accepted'
        ).first()
    return None