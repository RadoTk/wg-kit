from decimal import Decimal
from wagtail.images.models import Image
from django.core.files.base import ContentFile
from app.store.models import StoreProduct
from wagtail.models import Page

parent = Page.objects.filter(depth=2).first()

# Créer l'image
gif_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B'
image_file = ContentFile(gif_data, name='test.gif')
img = Image(title="Test Image", file=image_file)
img.save()

# Créer le produit correctement
product = StoreProduct(
   title="Test Product",
   image=img,
   price_usd=Decimal('9.99')  # valide pour DecimalField
)

# Ajouter à la page parent
parent.add_child(instance=product)

# Publier
product.save_revision().publish()

# Supprimer l'image
img.delete()

# Vérifier
product.refresh_from_db()
print("Image du produit après suppression :", product.image)  # None si SET_NULL

