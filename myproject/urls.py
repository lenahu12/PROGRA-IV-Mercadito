from django.contrib import admin
from django.urls import path, include
from .views import home_view
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/scraping/', include('scraping.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

