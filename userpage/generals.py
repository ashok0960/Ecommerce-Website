from .models import *
from django.conf import settings


def setting(request):
    data = {
        'ecom' : Setting.objects.last(),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return data