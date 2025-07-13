from django.contrib import admin
from django.urls import path, include
from .views import AnalizeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('analize/', AnalizeView.as_view(), name='analize'),
]
