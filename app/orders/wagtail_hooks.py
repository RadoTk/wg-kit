from wagtail.admin.viewsets.model import ModelViewSet
from wagtail import hooks
from .models import Order, OrderStatus
from django.utils.html import format_html


class OrderViewSet(ModelViewSet):
    model = Order
    menu_label = "Orders"
    menu_icon = "doc-full"
    menu_order = 200
    add_to_admin_menu = True

    add_view_enabled = False
    edit_view_enabled = True


    form_fields = ["status"]  

    inspect_view_enabled = True
    inspect_view_fields = [
        "get_items_html_table",
    ]

    list_display = [
        "id", 
        "get_colored_status_display",  
        "get_colored_payment_status",
        "shopper_full_name", 
        "shopper_email", 
        "shopper_address",
        "shopper_country", 
        "created_at", 
        "get_admin_items_link"
    ]
    
    list_filter = ["status"]
    search_fields = ["shopper_name", "shopper_email", "shopper_first_name"]

    icon = "doc-full" 
    header_icon = "doc-full"


@hooks.register("register_admin_viewset")
def register_order_viewset():
    return OrderViewSet()


@hooks.register('construct_main_menu')
def display_order_notification_badge(request, menu_items):
    try:
        new_order_status = OrderStatus.objects.get(code='new', is_active=True)
        new_orders_count = Order.objects.filter(status=new_order_status).count()
    except OrderStatus.DoesNotExist:
        new_orders_count = 0
    except Exception:
        new_orders_count = 0

    for item in menu_items:
        if item.name == 'orders':
            original_label = "Orders"  
            if new_orders_count > 0:
                item.label = f"{original_label} 🔴 {new_orders_count}"
            else:
                item.label = original_label
            break



@hooks.register('insert_global_admin_js')
def global_admin_js():
    return format_html('<script src="/static/js/admin_notifications.js"></script>')
