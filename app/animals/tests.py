from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Animal


User = get_user_model()


class AnimalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')

    def test_create_animal(self):
        a = Animal.objects.create(name='Rex', category='dog', owner=self.user)
        self.assertEqual(str(a), 'Rex (Chien)')

    def test_invalid_age(self):
        with self.assertRaises(Exception):
            Animal.objects.create(name='Oldie', category='cat', age_years=500)


