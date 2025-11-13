import stripe

from decimal import Decimal
from django.shortcuts import redirect, render
from app.cart.cart import Cart
from app.orders.forms import OrderCreateForm
from .models import Order, OrderItem, OrderStatus
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings

from .webhooks import stripe_webhook

stripe.api_key = settings.STRIPE_SECRET_KEY



def add_items_to_order(order: Order, cart: Cart) -> None:
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product_title=getattr(item["product"], "title", "Produit inconnu"),
            product_id=item["product"].id,
            price=item["price"],
            quantity=item["quantity"],
        )



def order_create(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    shipping_cost = Decimal("0.00")
    subtotal = cart.get_cart_subtotal()
    total = subtotal + shipping_cost

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            add_items_to_order(order, cart)
            cart.clear()

            # ✅ Création session Stripe
            line_items = []
            for item in order.items.all():
                line_items.append({
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": item.product_title,
                        },
                        "unit_amount": int(item.price * 100),  # en centimes
                    },
                    "quantity": item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri('/orders/thanks/'),
                cancel_url=request.build_absolute_uri('/cart/'),
                metadata={
                    'order_id': str(order.id),
                }
            )

            return redirect(session.url, code=303)

    else:
        form = OrderCreateForm()

    return render(
        request,
        "orders/create.html",
        {
            "cart": cart,
            "form": form,
            "shipping_cost": shipping_cost,
            "subtotal": subtotal,
            "total": total,
        }
    )


def order_success_view(request):
    return render(request, 'orders/success.html')



def get_new_orders_count(request):
    status = OrderStatus.objects.filter(code='new', is_active=True).first()
    count = Order.objects.filter(status=status).count() if status else 0
    return JsonResponse({'count': count})

