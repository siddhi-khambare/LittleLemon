
"""
URL configuration for littlelemon project.
Coursera Meta Back-End Developer Capstone Project.
"""

import importlib.util

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from restaurant import views


# Coursera-compatible Booking API
# URL: /restaurant/booking/tables/

coursera_router = DefaultRouter()
coursera_router.register(
    r'tables',
    views.BookingViewSet,
    basename='tables'
)


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Website Pages
    path('', views.index, name='home'),
    path('about/', views.about_page, name='about'),
    path('menu/', views.menu_page, name='menu'),
    path('reservations/', views.reservations_page, name='reservations'),
    path('order/', views.order_page, name='order'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register-page'),
    path('contact/', views.contact_page, name='contact-page'),

    # Main REST API
    path('api/', include('restaurant.urls')),

    # Coursera Booking API
    # Keep this before the general restaurant include
    path(
        'restaurant/booking/',
        include(coursera_router.urls)
    ),

    # Coursera Restaurant API
    path('restaurant/', include('restaurant.urls')),

    # Token Authentication
    path(
        'api-token-auth/',
        obtain_auth_token,
        name='api-token-auth'
    ),
]


# Optional Djoser Authentication
if importlib.util.find_spec('djoser') is not None:
    urlpatterns += [
        path('auth/', include('djoser.urls')),
        path('auth/', include('djoser.urls.authtoken')),
    ]
