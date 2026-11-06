"""
URL configuration for littlelemon project.
Coursera Meta Back-End Developer Capstone Project
"""
import importlib.util

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from restaurant import views

# Coursera-style booking path: /restaurant/booking/tables/
coursera_router = DefaultRouter()
coursera_router.register(r'tables', views.BookingViewSet, basename='tables')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Website pages
    path('', views.index, name='home'),
    path('about/', views.about_page, name='about'),
    path('menu/', views.menu_page, name='menu'),
    path('reservations/', views.reservations_page, name='reservations'),
    path('order/', views.order_page, name='order'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register-page'),
    path('contact/', views.contact_page, name='contact-page'),

    # REST API
    path('api/', include('restaurant.urls')),

    # Coursera-compatible paths (/restaurant/menu/, /restaurant/booking/tables/)
    path('restaurant/', include('restaurant.urls')),
    path('restaurant/booking/', include(coursera_router.urls)),
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='root-api-token-auth'),
]

# Optional Djoser paths (/auth/users/, /auth/token/login/)
if importlib.util.find_spec('djoser') is not None:
    urlpatterns += [
        path('auth/', include('djoser.urls')),
        path('auth/', include('djoser.urls.authtoken')),
    ]
