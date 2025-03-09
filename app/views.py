from django.shortcuts import render
from store.models import Product, ReviewRating, ProductGalary
from django.views.generic import DetailView
from orders.models import OrderProduct,Account
from django.http import JsonResponse
from django.core.cache import cache
import random

def get_random_products():
    all_products = list(Product.objects.all())
    return random.sample(all_products, min(4, len(all_products)))

def home(request):
    products = Product.objects.all().filter(is_available=True)
    recommended_products = get_random_products()
    context = {
        'products': products,
        'recommended_products': recommended_products
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, product_id=None, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['reviews'] = ReviewRating.objects.filter(product_id=self.object.id, status=True)
        context['product_galary'] = ProductGalary.objects.filter(product_id=self.object.id)
        context['all_products'] = Product.objects.all()[0:4]

        if self.request.user.is_authenticated:
            try:
                context['orderproduct'] = OrderProduct.objects.filter(user=self.request.user,
                                                                      product_id=self.object.id).exists()
            except OrderProduct.DoesNotExist:
                orderproduct = None
        else:
            orderproduct = None

        return context

# views.py
from django.shortcuts import redirect
from django.utils.translation import activate
from django.http import HttpResponse
from django.utils.translation import get_language

def set_language_from_request(request):
    language_code = request.GET.get('lang', None)

    if language_code:
        activate(language_code)
        current_language = get_language()  # Get the current language
        response = HttpResponse(f"Language changed to {current_language}.")
    else:
        response = HttpResponse("No language code provided.")
    
    return response

from django.shortcuts import render
from .models import StoreProduct, UserProfile, Account

from django.http import JsonResponse
from django.core.serializers import serialize

def live_market_prices(request):
    user = request.user  # Get the logged-in user

    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    try:
        # Fetch user profile to get the city
        user_profile = UserProfile.objects.get(user=user)
        city = user_profile.city

        # Fetch farmer's products and their prices
        farmer_products = StoreProduct.objects.filter(farmer=user)

        # Serialize products into JSON
        products_data = list(farmer_products.values('id', 'name', 'price'))  # Adjust fields as needed

        response_data = {
            'city': city,
            'farmer_products': products_data
        }

        return JsonResponse(response_data, safe=False)

    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=404)








