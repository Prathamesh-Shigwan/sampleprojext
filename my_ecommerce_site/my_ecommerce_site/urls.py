from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from products.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('accounts.urls')),  # Include accounts URLs just once
    path('blog/', include('blog.urls')),
    path('tinymce/', include('tinymce.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)