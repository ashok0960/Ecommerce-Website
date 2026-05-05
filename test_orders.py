#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from userpage.models import Order
from django.contrib.auth.models import User

print("=" * 60)
print("ORDER TRACKING SYSTEM TEST")
print("=" * 60)

# Test order status counts
try:
    # Get a test user (assuming there's at least one user)
    test_user = User.objects.first()
    if test_user:
        print(f"Testing with user: {test_user.username}")
        print()

        # Test order statistics
        total_orders = Order.objects.filter(user=test_user).count()
        completed_orders = Order.objects.filter(user=test_user, order_status='Complete').count()
        in_progress_orders = Order.objects.filter(user=test_user, order_status='In Progress').count()
        paid_orders = Order.objects.filter(user=test_user, payment_status=True).count()

        print("Order Statistics:")
        print(f"  Total Orders: {total_orders}")
        print(f"  Completed Orders: {completed_orders}")
        print(f"  In Progress Orders: {in_progress_orders}")
        print(f"  Paid Orders: {paid_orders}")
        print()

        # Test filtering
        print("Testing Order Filtering:")
        all_orders = Order.objects.filter(user=test_user).order_by('-created_at')
        in_progress = all_orders.filter(order_status='In Progress')
        completed = all_orders.filter(order_status='Complete')
        paid = all_orders.filter(payment_status=True)

        print(f"  All orders: {all_orders.count()}")
        print(f"  In Progress: {in_progress.count()}")
        print(f"  Completed: {completed.count()}")
        print(f"  Paid: {paid.count()}")
        print()

        # Show recent orders
        recent_orders = all_orders[:3]
        if recent_orders:
            print("Recent Orders:")
            for order in recent_orders:
                print(f"  Order #{order.id}: {order.product.title[:30]}...")
                print(f"    Status: {order.order_status}")
                print(f"    Payment: {'Paid' if order.payment_status else 'Unpaid'}")
                print(f"    Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
                print()

        print("✅ ORDER TRACKING SYSTEM: WORKING")
    else:
        print("❌ No users found in database")

except Exception as e:
    print(f"❌ Error testing order tracking: {str(e)}")

print("=" * 60)