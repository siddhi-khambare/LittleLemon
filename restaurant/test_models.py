
from django.test import TestCase
from .models import Menu


class MenuModelTest(TestCase):
    """Unit test for Menu model string representation."""

    def test_get_item(self):
        item = Menu.objects.create(
            title="IceCream",
            price=80.00,
            inventory=100
        )

        self.assertEqual(str(item), "IceCream : 80.0")
        self.assertEqual(item.get_item(), "IceCream : 80.0")
