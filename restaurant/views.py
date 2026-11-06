from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status, viewsets
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, ContactMessage, Menu
from .serializers import (
    BookingSerializer,
    ContactMessageSerializer,
    MenuSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Website pages (HTML). ensure_csrf_cookie makes sure the browser receives a
# csrftoken cookie so JavaScript fetch() calls can send X-CSRFToken.
# ---------------------------------------------------------------------------

def _page(template_name, active):
    @ensure_csrf_cookie
    def view(request):
        context = {
            'active_page': active,
            'current_year': datetime.now().year,
        }
        return render(request, template_name, context)
    view.__name__ = f'{active}_page'
    return view


index = _page('index.html', 'home')
about_page = _page('about.html', 'about')
menu_page = _page('menu.html', 'menu')
reservations_page = _page('reservations.html', 'reservations')
order_page = _page('order.html', 'order')
login_page = _page('login.html', 'login')
register_page = _page('register.html', 'register')
contact_page = _page('contact.html', 'contact')


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

class IsAdminOrReadOnly(BasePermission):
    """Anyone can read; only staff users can create/update/delete."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """Object-level: staff can access any booking, users only their own."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user_id == request.user.id


# ---------------------------------------------------------------------------
# Menu API
# ---------------------------------------------------------------------------

class MenuItemsView(generics.ListCreateAPIView):
    """
    GET  /api/menu/                 -> list menu items (public)
         ?category=starters|main|desserts|drinks
         ?featured=true
    POST /api/menu/                 -> create menu item (staff only)
    """
    serializer_class = MenuSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Menu.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        featured = self.request.query_params.get('featured')
        if featured is not None and featured.lower() in ('1', 'true', 'yes'):
            queryset = queryset.filter(featured=True)
        return queryset


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/menu/<id>/  -> retrieve (public)
    PUT    /api/menu/<id>/  -> update (staff only)
    PATCH  /api/menu/<id>/  -> partial update (staff only)
    DELETE /api/menu/<id>/  -> delete (staff only)
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAdminOrReadOnly]


# ---------------------------------------------------------------------------
# Booking API
# ---------------------------------------------------------------------------

class BookingViewSet(viewsets.ModelViewSet):
    """
    POST   /api/booking/       -> create booking (guests allowed; user attached if logged in)
    GET    /api/booking/       -> list bookings (staff: all, customers: their own)
    GET    /api/booking/<id>/  -> retrieve (owner or staff)
    PUT    /api/booking/<id>/  -> update (owner or staff)
    DELETE /api/booking/<id>/  -> cancel (owner or staff)
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Booking.objects.all()
        if user.is_authenticated:
            return Booking.objects.filter(user=user)
        return Booking.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user if user.is_authenticated else None)


# ---------------------------------------------------------------------------
# Users & Authentication API
# ---------------------------------------------------------------------------

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class CustomAuthToken(ObtainAuthToken):
    """
    POST /api/api-token-auth/ -> Authenticate credentials and return token + is_staff flag
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff or user.is_superuser
        })


class UserViewSet(viewsets.ModelViewSet):
    """Staff-only API endpoint to view or manage registered users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserRegistrationView(generics.CreateAPIView):
    """POST /api/register/ -> register a new customer account."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class CurrentUserView(APIView):
    """GET /api/me/ -> return the user that owns the supplied token."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data['is_staff'] = request.user.is_staff
        return Response(data)


class TokenLogoutView(APIView):
    """POST /api/logout/ -> delete the user's auth token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response(
            {"message": "Logged out successfully. Token invalidated."},
            status=status.HTTP_200_OK
        )


# ---------------------------------------------------------------------------
# Contact API
# ---------------------------------------------------------------------------

class ContactMessageView(generics.ListCreateAPIView):
    """
    POST /api/contact/ -> submit a contact message (public, validated)
    GET  /api/contact/ -> list messages (staff only)
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminUser()]
