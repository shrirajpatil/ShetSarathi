from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.contrib import admin
from django.urls import path, include

# Define URLs for the project
urlpatterns = [
    path('admin/', admin.site.urls),
    path('setlang/', set_language, name='set_language'),  # This should be outside i18n_patterns
    path('', include('app.urls')),  # Your app URLs
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('farmer/', include('farmer.urls')),
    path('orders/', include('orders.urls')),
    path('community/', include('community.urls')),
     path('chatbot/', include('openai_chatbot.urls')),


    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wrapping URLs with i18n_patterns for language prefixing
urlpatterns += i18n_patterns(
    # Optionally include other URLs that should be wrapped with language codes
    # Example:
    # path('blog/', include('blog.urls')),
)
