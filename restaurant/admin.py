from django.contrib import admin
from .models import Booking, ContactMessage, Menu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'inventory', 'featured')
    list_filter = ('category', 'featured')
    list_editable = ('price', 'inventory', 'featured')
    search_fields = ('title', 'description')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'no_of_guests', 'booking_date', 'user')
    list_filter = ('booking_date',)
    search_fields = ('name', 'user__username')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
