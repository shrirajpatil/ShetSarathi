import googlemaps
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem, NegotiationRequest
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.conf import settings

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def calculate_transportation_cost(farmer_city, buyer_city, quantity):
    try:
        if not farmer_city or farmer_city == "Unknown" or not buyer_city or buyer_city == "Unknown":
            return Decimal('50') * quantity
        result = gmaps.distance_matrix(farmer_city, buyer_city, mode="driving", units="metric")
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000
            return Decimal(str(distance * 0.1 * quantity))
        else:
            return Decimal('50') * quantity
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return Decimal('50') * quantity

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=current_user, product=product)
            if cart_item.quantity + 1 <= product.quantity:
                cart_item.quantity += 1
                cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity + 1 <= product.quantity:
                cart_item.quantity += 1
                cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
        return redirect('cart')

def remove_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=current_user)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')

def remove_cart_item(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=current_user)
        cart_item.delete()
        return redirect('cart')
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
        return redirect('cart')

@login_required(login_url='login')
def negotiate_bulk(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(user=request.user, product=product, is_active=True).first()
    if request.method == 'POST':
        proposed_price = request.POST.get('proposed_price')
        quantity = cart_item.quantity if cart_item else int(request.POST.get('quantity', 1))
        if proposed_price:
            NegotiationRequest.objects.create(
                buyer=request.user,
                product=product,
                proposed_price=Decimal(proposed_price),
                quantity=quantity,
                status='Pending'
            )
            return redirect('cart')
        else:
            return render(request, 'store/negotiate_bulk.html', {'product': product, 'cart_item': cart_item, 'error': 'Please enter a proposed price'})
    return render(request, 'store/negotiate_bulk.html', {'product': product, 'cart_item': cart_item})

def cart(request, total=0, quantity=0, cart_items=None, transport_cost=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            buyer_city = request.user.userprofile.city if hasattr(request.user, 'userprofile') else "Unknown"
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            buyer_city = "Unknown"

        total = Decimal('0')
        transport_cost = Decimal('0')
        for cart_item in cart_items:
            total += cart_item.sub_total()  # Use sub_total directly
            quantity += cart_item.quantity
            farmer_city = cart_item.product.city or "Unknown"
            transport_cost += calculate_transportation_cost(farmer_city, buyer_city, cart_item.quantity)
        
        grand_total = total + transport_cost

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'transport_cost': transport_cost,
        'grand_total': grand_total,
    }
    request.session['grand_total'] = str(grand_total)
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None, transport_cost=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            buyer_city = request.POST.get("city", request.user.userprofile.city if hasattr(request.user, 'userprofile') else "Unknown")
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            buyer_city = "Unknown"

        total = Decimal('0')
        transport_cost = Decimal('0')
        for cart_item in cart_items:
            total += cart_item.sub_total()  # Use sub_total directly
            quantity += cart_item.quantity
            farmer_city = cart_item.product.city or "Unknown"
            transport_cost += calculate_transportation_cost(farmer_city, buyer_city, cart_item.quantity)
        
        grand_total = total + transport_cost
        grand_total_in_cents = int(grand_total * 100)

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'transport_cost': transport_cost,
        'grand_total': grand_total,
        'grand_total_in_cents': grand_total_in_cents,
    }
    request.session['grand_total'] = str(grand_total)
    return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def negotiation_status(request):
    requests = NegotiationRequest.objects.filter(buyer=request.user)
    context = {'requests': requests}
    return render(request, 'store/negotiation_status.html', context)