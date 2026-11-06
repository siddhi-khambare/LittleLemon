"""API URL patterns for the restaurant app (mounted under /api/ and /restaurant/)."""
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'booking', views.BookingViewSet, basename='booking')

urlpatterns = [
    # Menu
    path('menu/', views.MenuItemsView.as_view(), name='menu-list'),
    path('menu/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu-detail'),
    path('menu/<int:pk>', views.SingleMenuItemView.as_view()),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),

    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='api-token-auth'),
    path('logout/', views.TokenLogoutView.as_view(), name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),

    # Contact
    path('contact/', views.ContactMessageView.as_view(), name='contact'),

    # Booking (router: /booking/ and /booking/<id>/)
    path('', include(router.urls)),
]
