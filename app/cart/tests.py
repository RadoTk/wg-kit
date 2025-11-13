from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from wagtail.models import Page
from app.store.models import StoreProduct, StoreProductIndexPage
from app.cart.models import CartItem
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.sessions.middleware import SessionMiddleware
from app.cart.cart import Cart, FakeProduct


class FakeProduct:
    """Produit factice pour tester le panier sans Wagtail."""
    _id_counter = 1

    def __init__(self, title, price, is_available=True):
        self.title = title
        self.price = price       # ⚠ correspond à Cart.add()
        self.id = FakeProduct._id_counter
        FakeProduct._id_counter += 1
        self.is_available = is_available



User = get_user_model()

class CartTestCase(TestCase):
    def setUp(self):
        # Initialisation de RequestFactory pour simuler les requêtes
        self.factory = RequestFactory()

        # Création d'un utilisateur pour les tests authentifiés
        self.user = User.objects.create_user(username="testuser", password="password")

        # Récupération de la page racine Wagtail
        self.root_page = Page.objects.get(id=1)

        # Création de la page d'index de la boutique
        self.product_index = StoreProductIndexPage(title="Store", slug="store")
        self.root_page.add_child(instance=self.product_index)
        self.product_index.save()

        # Création de produits pour les tests
        self.product1 = StoreProduct(
            title="Test Product 1",
            slug="test-product-1",
            price_usd=Decimal("10.00")  
        )
        self.product_index.add_child(instance=self.product1)
        self.product1.save()

        self.product2 = StoreProduct(
            title="Test Product 2",
            slug="test-product-2",
            price_usd=Decimal("20.00")  
        )
        self.product_index.add_child(instance=self.product2)
        self.product2.save()


    def test_cart_session_add_item(self):
        request = self.factory.get("/")
        request.session = {}
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        items = cart.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 2)
        self.assertEqual(items[0]["total_price"], Decimal("20.00"))

    def test_cart_db_add_item_authenticated(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {}
        cart = Cart(request)

        cart.add(self.product2, quantity=3)
        self.assertEqual(CartItem.objects.count(), 1)
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.get_total_price(), Decimal("60.00"))

    def test_cart_remove_item(self):
        request = self.factory.get("/")
        request.session = {}
        cart = Cart(request)
        cart.add(self.product1, quantity=1)
        cart.remove(self.product1)
        self.assertEqual(len(cart.get_items()), 0)

    def test_cart_clear(self):
        request = self.factory.get("/")
        request.session = {}
        cart = Cart(request)
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=2)
        cart.clear()
        self.assertEqual(len(cart.get_items()), 0)

    def test_cart_subtotal_and_total(self):
        request = self.factory.get("/")
        request.session = {}
        cart = Cart(request)
        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)
        subtotal = cart.get_cart_subtotal()
        total = cart.get_cart_total()
        self.assertEqual(subtotal, Decimal("40.00"))
        self.assertEqual(total, Decimal("40.00"))



class CartErrorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        # Ajoute une session valide à la requête
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()
        self.cart = Cart(self.request)

        self.product = FakeProduct("Produit Test", price=10.00)


    def test_add_negative_quantity_raises(self):
        """Ajouter une quantité négative doit lever une ValueError"""
        with self.assertRaises(ValueError):
            self.cart.add(self.product, quantity=-1)

    def test_remove_nonexistent_product(self):
        """Supprimer un produit qui n'est pas dans le panier ne doit rien faire"""
        self.cart.remove(self.product)
        self.assertEqual(len(self.cart.get_items()), 0)

    def test_add_unavailable_product(self):
        """Ajouter un produit indisponible doit lever une ValueError"""
        self.product.is_available = False
        with self.assertRaises(ValueError):
            self.cart.add(self.product, quantity=1)
