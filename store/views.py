import random
from django.shortcuts import get_object_or_404, render, redirect
from store.models import Product, ReviewRating
from category.models import Category
from .forms import ReviewForms, ProductSortForm, CatSortForm
from django.contrib import messages

from django.shortcuts import render
from store.models import Product
from category.models import Category

def store(request, category_slug=None):
    # Get all available products (unfiltered)
    products = Product.objects.filter(is_available=True)
    filtered_products = None
    
    # Get filter parameters
    state = request.GET.get('state', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    # Apply filtering if either state or category is selected
    if state or category:
        filtered_products = Product.objects.filter(is_available=True)
        
        if state:
            filtered_products = filtered_products.filter(state=state)
        if category:
            filtered_products = filtered_products.filter(category__category_name__iexact=category)
            
        # Apply sorting to filtered products
        if sort:
            if sort == 'new':
                filtered_products = filtered_products.order_by('-created_date')
            elif sort == 'price_low_to_high':
                filtered_products = filtered_products.order_by('price')
            elif sort == 'price_high_to_low':
                filtered_products = filtered_products.order_by('-price')

    # Get all states for dropdown (you might want to create a separate State model)
    states = Product.objects.values_list('state', flat=True).distinct()

    context = {
        'products': products,
        'filtered_products': filtered_products,
        'states': states,
        'selected_state': state,
        'selected_category': category,
        'selected_sort': sort,
    }
    return render(request, 'store/store.html', context)

 

def submit_reviews(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForms(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you, your Review has been updated')
            return redirect(url)


        except ReviewRating.DoesNotExist:
            form = ReviewForms(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you, your Review has been submitted')
                return redirect(url)


def get_random_products():
    all_products = list(Product.objects.all())
    random.shuffle(all_products)
    return all_products

def get_recommendations(request):
    product_names = ["Potatoes", "Wheat", "Broccoli", "Carrots", "Onions"]
    recommendations = list(Product.objects.filter(product_name__in=product_names))
    random.shuffle(recommendations)

    context = {
        'recommendations': recommendations
    }
    return render(request, 'store/recommended_products.html', context)

def sortProducts(request):
    return store(request)

def catProducts(request):
    return store(request)

def apply_sorting(queryset, sort_by):
    # Apply sorting logic based on the 'sort_by' parameter
    if sort_by == 'new':
        return queryset.order_by('-created_date')
    elif sort_by == 'price_low_to_high':
        print('enterd')
        return queryset.order_by('price')
    elif sort_by == 'price_high_to_low':
        return queryset.order_by('-price')
    elif sort_by == 'category':
        return queryset.order_by('-category')
    else:
        return queryset  # Default sorting



def apply_catsorting(queryset, sort_by):
    if sort_by == 'allproducts':
        return queryset
    elif sort_by == 'fruits':
        category = get_object_or_404(Category, category_name='Fruits')
        return queryset.filter(category=category.id)
    elif sort_by == 'grains':
        category = get_object_or_404(Category, category_name='Grains')
        return queryset.filter(category=category.id)
    elif sort_by == 'seeds':
        category = get_object_or_404(Category, category_name='Seeds')
        return queryset.filter(category=category.id)
    elif sort_by == 'vegetable':
        category = get_object_or_404(Category, category_name='Vegetables')
        return queryset.filter(category=category.id)
    else:
        return queryset.none()  # Return an empty queryset if 'sort_by' is not recognized
