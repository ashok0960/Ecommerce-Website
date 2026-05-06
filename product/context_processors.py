from .models import Product
from userpage.models import Order

def pending_orders_context(request):
    context = {
        'pending_orders_count': 0
    }

    if request.user.is_authenticated and request.user.is_staff:
        if request.user.is_superuser:
            pending_orders = Order.objects.filter(
                order_status__in=['In Progress', 'way to deliver']
            ).count()
        else:
            vendor_product_ids = Product.objects.filter(
                user=request.user
            ).values_list('id', flat=True)
            pending_orders = Order.objects.filter(
                product_id__in=vendor_product_ids,
                order_status__in=['In Progress', 'way to deliver']
            ).count()

        context['pending_orders_count'] = pending_orders

    return context
