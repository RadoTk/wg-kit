from wagtail.snippets.models import register_snippet
from wagtail.admin.viewsets.model import ModelViewSet
from .models import GenericPageLink

class GenericPageLinkViewSet(ModelViewSet):
    model = GenericPageLink
    menu_label = "Liens externes"
    menu_icon = "link"
    list_display = ("title", "url")
    search_fields = ("title",)

register_snippet(GenericPageLinkViewSet)
