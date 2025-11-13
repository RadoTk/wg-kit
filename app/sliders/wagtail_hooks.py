from wagtail import hooks
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.userbar import AccessibilityItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from app.sliders.filters import RevisionFilterSetMixin

from app.sliders.models import Slide, Slider
from app.sliders.models.slider_placement import SliderPlacement


"""
N.B. To see what icons are available for use in Wagtail menus and StreamField block types,
enable the styleguide in settings:

INSTALLED_APPS = (
   ...
   'wagtail.contrib.styleguide',
   ...
)

or see https://thegrouchy.dev/general/2015/12/06/wagtail-streamfield-icons.html

This demo project also includes the wagtail-font-awesome-svg package, allowing further icons to be
installed as detailed here: https://github.com/allcaps/wagtail-font-awesome-svg#usage
"""


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "wagtailfontawesomesvg/solid/suitcase.svg",
        "wagtailfontawesomesvg/solid/utensils.svg",
    ]


class CustomAccessibilityItem(AccessibilityItem):
    axe_run_only = None


@hooks.register("construct_wagtail_userbar")
def replace_userbar_accessibility_item(request, items, page):
    items[:] = [
        CustomAccessibilityItem() if isinstance(item, AccessibilityItem) else item
        for item in items
    ]





class SlideViewSet(SnippetViewSet):
    model = Slide
    icon = "image"
    menu_label = "Slides"
    list_display = ("title", "subtitle")
    search_fields = ("title", "subtitle")

class SliderViewSet(SnippetViewSet):
    model = Slider
    icon = "folder-open-inverse"
    menu_label = "Sliders"
    list_display = ("name", "description")






class SliderPlacementViewSet(SnippetViewSet):
    model = SliderPlacement
    icon = "site"
    menu_label = "Placements"
    list_display = ("page", "slider", "position")
    search_fields = ("page__title", "slider__name", "position")


class SliderAdminGroup(SnippetViewSetGroup):
    menu_label = "Sliders"
    menu_icon = "image"
    items = (SlideViewSet, SliderViewSet, SliderPlacementViewSet)


register_snippet(SliderAdminGroup)
