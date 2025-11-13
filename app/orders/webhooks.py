import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from django.conf import settings
from .models import Order
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    """Webhook Stripe pour la gestion des paiements"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')

            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.mark_as_paid()
                except Order.DoesNotExist:
                    logger.warning(f"Order {order_id} non trouvé")
                except Exception as e:
                    logger.exception(f"Erreur mark_as_paid pour order {order_id}: {e}")
                    return HttpResponse(status=500)


    except ValueError as e:
        logger.exception(f"Erreur lecture payload Stripe: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning(f"Signature invalide Stripe: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.exception(f"Erreur webhook Stripe inconnue: {e}")
        return HttpResponse(status=500)

    return HttpResponse(status=200)
