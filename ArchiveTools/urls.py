from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from .views import extractMetadata
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("compareHash", views.compareHash, name="compareHash"), 
    path("generetaHash", views.generetaHash, name="generetaHash"), 
    path("viewFormat", views.viewFormat, name="viewFormat"), 
    path("", extractMetadata, name="extractMetadata"), 

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)