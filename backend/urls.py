# from django.contrib import admin
# from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('authentication.urls')),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]
# backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),  # 👈 This line includes your app's URLs
]
