from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.images import get_image_model
from wagtail.models import Page
from app.store.models import StoreProduct, StoreProductIndexPage

class OnDeleteCrashTests(TestCase):
    def setUp(self):
        Image = get_image_model()
        # Créer un faux fichier image en mémoire
        self.image_file = SimpleUploadedFile(
            name='fake.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00',
            content_type='image/jpeg'
        )
        self.image = Image.objects.create(
            title="Fake Image",
            file=self.image_file,
        )

        # Créer un index de produits
        self.index = StoreProductIndexPage(title="Index Test")
        Page.get_first_root_node().add_child(instance=self.index)

        # Créer un produit
        self.product = StoreProduct(
            title="Produit Test",
            price_usd=10.0,
            image=self.image,
        )
        self.index.add_child(instance=self.product)

    def test_delete_image_sets_null(self):
        """Vérifie que la suppression d'une image ne crash pas et met image=None"""
        self.image.delete()
        self.product.refresh_from_db()
        self.assertIsNone(self.product.image)

    def test_delete_parent_page_does_not_crash(self):
        """Test volontairement la suppression de la page parent"""
        self.index.delete()
        # Si on arrive ici, ça n'a pas crashé
        self.assertTrue(True)
