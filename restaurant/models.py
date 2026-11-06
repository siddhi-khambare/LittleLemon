from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    name = models.CharField(max_length=255)
    no_of_guests = models.IntegerField(default=6)
    booking_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['booking_date']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self):
        return f"{self.name} ({self.no_of_guests} guests) - {self.booking_date}"


class Menu(models.Model):
    CATEGORY_STARTERS = 'starters'
    CATEGORY_MAIN = 'main'
    CATEGORY_DESSERTS = 'desserts'
    CATEGORY_DRINKS = 'drinks'
    CATEGORY_CHOICES = [
        (CATEGORY_STARTERS, 'Starters'),
        (CATEGORY_MAIN, 'Main Course'),
        (CATEGORY_DESSERTS, 'Desserts'),
        (CATEGORY_DRINKS, 'Drinks'),
    ]

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField(default=5)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_MAIN,
    )
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=500, blank=True, default='')
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        verbose_name = 'Menu'
        verbose_name_plural = 'Menu Items'

    def get_item(self):
        return f'{self.title} : {str(self.price)}'

    def __str__(self):
        return f'{self.title} : {str(self.price)}'


# Alias for compatibility with MenuItem naming convention
MenuItem = Menu


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.subject or 'No subject'}"
