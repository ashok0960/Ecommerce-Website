#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

import stripe
from django.conf import settings

print("=" * 60)
print("STRIPE CONFIGURATION TEST")
print("=" * 60)

# Check if keys are loaded
print(f"\n✓ STRIPE_SECRET_KEY: {settings.STRIPE_SECRET_KEY[:20]}..." if settings.STRIPE_SECRET_KEY else "✗ STRIPE_SECRET_KEY: EMPTY")
print(f"✓ STRIPE_PUBLIC_KEY: {settings.STRIPE_PUBLIC_KEY[:20]}..." if settings.STRIPE_PUBLIC_KEY else "✗ STRIPE_PUBLIC_KEY: EMPTY")
print(f"✓ STRIPE_CURRENCY: {settings.STRIPE_CURRENCY}")

# Test Stripe API
stripe.api_key = settings.STRIPE_SECRET_KEY

try:
    # Attempt to verify the API key by retrieving account info
    acct = stripe.Account.retrieve()
    print(f"\n✓ STRIPE API CONNECTION: SUCCESS")
    print(f"  Account ID: {acct.id}")
    print(f"  Account Type: {acct.type}")
    print(f"  Email: {acct.email}")
except stripe.error.AuthenticationError as e:
    print(f"\n✗ STRIPE API ERROR: Authentication Failed")
    print(f"  Error: {str(e)}")
except Exception as e:
    print(f"\n✗ STRIPE API ERROR: {type(e).__name__}")
    print(f"  Error: {str(e)}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
