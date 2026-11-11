
"""
URL patterns for the restaurant application.
Mounted under /api/ and /restaurant/.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views


# Booking API Router
router = DefaultRouter()
router.register(
    r'booking',
    views.BookingViewSet,
    basename='booking'
)


urlpatterns = [

    # Menu API
    path(
        'menu/',
        views.MenuItemsView.as_view(),
        name='menu-list'
    ),
    path(
        'menu/<int:pk>/',
        views.SingleMenuItemView.as_view(),
        name='menu-detail'
    ),

    # Menu Items API
    path(
        'menu-items/',
        views.MenuItemsView.as_view(),
        name='menu-items-list'
    ),
    path(
        'menu-items/<int:pk>/',
        views.SingleMenuItemView.as_view(),
        name='menu-items-detail'
    ),

    # User Registration
    path(
        'register/',
        views.UserRegistrationView.as_view(),
        name='register'
    ),

    # Token Authentication
    path(
        'api-token-auth/',
        obtain_auth_token,
        name='api-token-auth'
    ),

    # Logout
    path(
        'logout/',
        views.TokenLogoutView.as_view(),
        name='logout'
    ),

    # Current User
    path(
        'me/',
        views.CurrentUserView.as_view(),
        name='current-user'
    ),

    # Contact API
    path(
        'contact/',
        views.ContactMessageView.as_view(),
        name='contact'
    ),

    # Booking API
    path('', include(router.urls)),
]
