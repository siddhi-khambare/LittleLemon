from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from .models import Booking, ContactMessage, Menu


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_username(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        # Run Django's built-in password validators (length, common, numeric, similarity)
        candidate = User(username=attrs.get('username'), email=attrs.get('email'))
        try:
            validate_password(attrs.get('password'), user=candidate)
        except Exception as exc:  # django.core.exceptions.ValidationError
            raise serializers.ValidationError({'password': list(getattr(exc, 'messages', [str(exc)]))})
        return attrs

    def create(self, validated_data):
        # create_user hashes the password - plain text is never stored
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )


class MenuSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Menu
        fields = [
            'id', 'title', 'price', 'inventory', 'category', 'category_display',
            'description', 'image_url', 'featured',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_inventory(self, value):
        if value < 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value


# Alias for compatibility with MenuItemSerializer
MenuItemSerializer = MenuSerializer


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Booking
        fields = ['id', 'user', 'name', 'no_of_guests', 'booking_date']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Please enter your full name.")
        return value

    def validate_no_of_guests(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        if value > 50:
            raise serializers.ValidationError("Number of guests cannot exceed 50 per booking.")
        return value

    def validate_booking_date(self, value):
        # Only enforce "future date" when creating a new booking
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Booking date and time must be in the future.")
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Please enter your name.")
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value
