# In your app's urls.py (e.g., app/urls.py)

from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from . import views
from .views import ProductDetailView
from django.views.i18n import set_language
from django.urls import path, include

urlpatterns = i18n_patterns(
    path('', views.home, name='header'),
)

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('about', views.about, name='about'),
    path('market-prices/', views.live_market_prices, name='market-prices'),
    path('i18n/', include('django.conf.urls.i18n')),
    
]
