"""
Seed the Little Lemon menu into the database.

Usage:
    python manage.py seed_menu

Safe to run multiple times: items are matched by title and updated in place.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import Menu

IMG = "https://images.unsplash.com/{}?auto=format&fit=crop&w=800&q=80"

MENU_ITEMS = [
    # Starters
    {
        "title": "Greek Salad",
        "category": Menu.CATEGORY_STARTERS,
        "price": Decimal("12.99"),
        "inventory": 25,
        "featured": True,
        "image_url": IMG.format("photo-1540189549336-e6e99c3679fe"),
        "description": "Crispy lettuce, peppers, olives and our Chicago-style feta cheese, "
                       "garnished with crunchy garlic and rosemary croutons.",
    },
    {
        "title": "Bruschetta",
        "category": Menu.CATEGORY_STARTERS,
        "price": Decimal("7.99"),
        "inventory": 30,
        "featured": True,
        "image_url": IMG.format("photo-1572695157366-5e585ab2b69f"),
        "description": "Grilled sourdough rubbed with garlic, topped with ripe tomatoes, "
                       "fresh basil, sea salt and extra-virgin olive oil.",
    },
    # Main Course
    {
        "title": "Pan-Seared Salmon",
        "category": Menu.CATEGORY_MAIN,
        "price": Decimal("24.50"),
        "inventory": 15,
        "featured": True,
        "image_url": IMG.format("photo-1467003909585-2f8a72700288"),
        "description": "Crispy-skin salmon over wilted spinach with a cucumber and tomato "
                       "relish and a light balsamic reduction.",
    },
    {
        "title": "Lemon Herb Risotto",
        "category": Menu.CATEGORY_MAIN,
        "price": Decimal("18.00"),
        "inventory": 20,
        "featured": False,
        "image_url": IMG.format("photo-1476124369491-e7addf5db371"),
        "description": "Creamy arborio rice slow-cooked with lemon zest, parmesan, "
                       "wild mushrooms and fresh garden herbs.",
    },
    {
        "title": "Slow-Grilled Lamb Ribs",
        "category": Menu.CATEGORY_MAIN,
        "price": Decimal("26.00"),
        "inventory": 12,
        "featured": False,
        "image_url": IMG.format("photo-1529193591184-b1d58069ecdd"),
        "description": "Tender lamb ribs marinated in oregano, garlic and lemon, "
                       "char-grilled and served with seasonal greens.",
    },
    # Desserts
    {
        "title": "Lemon Dessert",
        "category": Menu.CATEGORY_DESSERTS,
        "price": Decimal("6.50"),
        "inventory": 30,
        "featured": True,
        "image_url": IMG.format("photo-1519915028121-7d3463d20b13"),
        "description": "Straight from grandma's recipe book - every ingredient sourced "
                       "to be as authentic as can be imagined.",
    },
    {
        "title": "Classic Tiramisu",
        "category": Menu.CATEGORY_DESSERTS,
        "price": Decimal("7.50"),
        "inventory": 20,
        "featured": False,
        "image_url": IMG.format("photo-1571877227200-a0d98ea607e9"),
        "description": "Espresso-soaked ladyfingers layered with whipped mascarpone "
                       "and finished with a dusting of cocoa.",
    },
    {
        "title": "Orange Blossom Crepes",
        "category": Menu.CATEGORY_DESSERTS,
        "price": Decimal("6.99"),
        "inventory": 18,
        "featured": False,
        "image_url": IMG.format("photo-1519676867240-f03562e64548"),
        "description": "Delicate crepes with fresh orange, whipped cream, toasted "
                       "almonds and a drizzle of wildflower honey.",
    },
    # Drinks
    {
        "title": "Fresh Mint Lemonade",
        "category": Menu.CATEGORY_DRINKS,
        "price": Decimal("4.50"),
        "inventory": 50,
        "featured": False,
        "image_url": IMG.format("photo-1621263764928-df1444c5e859"),
        "description": "Freshly squeezed lemons and limes muddled with garden mint, "
                       "served over crushed ice.",
    },
    {
        "title": "Iced Lime Tea",
        "category": Menu.CATEGORY_DRINKS,
        "price": Decimal("3.99"),
        "inventory": 50,
        "featured": False,
        "image_url": IMG.format("photo-1556679343-c7306c1976bc"),
        "description": "House-brewed black tea chilled with lime and a hint of mint.",
    },
    {
        "title": "Espresso",
        "category": Menu.CATEGORY_DRINKS,
        "price": Decimal("2.99"),
        "inventory": 80,
        "featured": False,
        "image_url": IMG.format("photo-1510591509098-f4fdc6d0ff04"),
        "description": "A rich, velvety single shot pulled from our signature roast.",
    },
    {
        "title": "Chocolate Frappe",
        "category": Menu.CATEGORY_DRINKS,
        "price": Decimal("5.50"),
        "inventory": 40,
        "featured": False,
        "image_url": IMG.format("photo-1577805947697-89e18249d767"),
        "description": "Blended chocolate shake topped with whipped cream and cocoa.",
    },
]


class Command(BaseCommand):
    help = "Create or update the Little Lemon menu items (idempotent)."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for item in MENU_ITEMS:
            data = dict(item)
            title = data.pop("title")
            # Match case-insensitively so older rows like "Greek salad" are reused
            existing = Menu.objects.filter(title__iexact=title).first()
            if existing:
                for field, value in data.items():
                    setattr(existing, field, value)
                existing.title = title
                existing.save()
                updated_count += 1
            else:
                Menu.objects.create(title=title, **data)
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Menu seeded: {created_count} created, {updated_count} updated, "
            f"{Menu.objects.count()} total items."
        ))

