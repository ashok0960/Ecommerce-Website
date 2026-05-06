from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator
import stripe
import json
from django.conf import settings
from product.models import Product, Category
from .models import Cart, Order, Contact, Wishlist
from .forms import OrderForm, ContactForm

stripe.api_key = settings.STRIPE_SECRET_KEY

CHATBOT_RESPONSES = {
    'hello': 'Hello! Welcome to Ashok Store. How can I help you today?',
    'hi': 'Hi there! How can I assist you?',
    'order': 'You can track your orders by going to My Orders in your account menu.',
    'track': 'Go to My Orders from the top menu to track your order status.',
    'payment': 'We accept Cash on Delivery (COD) and Card payments via Stripe.',
    'stripe': 'For card payments we use Stripe secure checkout. If you face issues, ensure your card details are correct.',
    'cart': 'You can view your cart by clicking the Cart icon in the navigation bar.',
    'return': 'For returns or refunds, please contact us via the Contact page or email ashokkarki6677@gmail.com.',
    'refund': 'Refund requests are processed within 5-7 business days. Contact us at ashokkarki6677@gmail.com.',
    'shipping': 'We deliver across Nepal. Standard delivery takes 3-5 business days.',
    'delivery': 'Delivery typically takes 3-5 business days. COD orders are confirmed before dispatch.',
    'product': 'Browse all our products on the Products page. Use filters to find what you need!',
    'price': 'All prices are listed on the product pages. Discounted prices are shown in green.',
    'contact': 'You can reach us at ashokkarki6677@gmail.com or call 9810549380.',
    'help': 'I can help with orders, payments, shipping, returns, and products. What do you need?',
    'cancel': 'To cancel an order, please contact us immediately at ashokkarki6677@gmail.com.',
    'account': 'You can manage your account from the top-right dropdown menu after logging in.',
    'login': 'Click the Login button in the top-right corner to sign in to your account.',
    'register': 'Click Register in the top-right corner to create a new account.',
    'discount': 'Check our Products page for the latest discounts and offers!',
    'stock': 'Product availability is shown on each product page. Out-of-stock items are marked.',
    'wishlist': 'Click the Wishlist button on any product page to save it for later.',
    'bye': 'Goodbye! Have a great shopping experience at Ashok Store!',
    'thanks': 'You are welcome! Is there anything else I can help you with?',
    'thank you': 'You are welcome! Happy shopping!',
}


# ─── PUBLIC VIEWS ────────────────────────────────────────────────────────────

def index(request):
    context = {
        'products': Product.objects.filter(trending=True).order_by('-id')[:8],
        'new_arrivals': Product.objects.order_by('-id')[:6],
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')


def products(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    sort = request.GET.get('sort', '')

    all_products = Product.objects.all()

    if category_id:
        all_products = all_products.filter(category_id=category_id)
    if search_query:
        all_products = all_products.filter(
            Q(title__icontains=search_query) | Q(l_description__icontains=search_query)
        )
    if sort == 'price_asc':
        all_products = all_products.order_by('discounted_price')
    elif sort == 'price_desc':
        all_products = all_products.order_by('-discounted_price')
    elif sort == 'newest':
        all_products = all_products.order_by('-id')
    else:
        all_products = all_products.order_by('-id')

    paginator = Paginator(all_products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'selected_categories': int(category_id) if category_id else None,
        'search_query': search_query,
        'sort': sort,
        'total_count': all_products.count(),
    }
    return render(request, 'products.html', context)


def productDetails(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    context = {
        'item': product,
        'related': related,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'product_details.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=f"Contact: {form.cleaned_data['subject']}",
                    message=f"Name: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\n\n{form.cleaned_data['message']}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ─── CART ────────────────────────────────────────────────────────────────────

@login_required
def addtocart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if Cart.objects.filter(user=request.user, product=product).exists():
        messages.error(request, 'Item already in cart.')
    else:
        Cart.objects.create(user=request.user, product=product)
        messages.success(request, f'{product.title} added to cart!')
    return redirect('productdetails', product_id)


@login_required
def cart(request):
    cartitems = Cart.objects.filter(user=request.user).select_related('product')
    total = sum(item.product.discounted_price for item in cartitems)
    return render(request, 'allcarts.html', {'cartitems': cartitems, 'total': total})


@login_required
def delete_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ─── ORDERS ──────────────────────────────────────────────────────────────────

@login_required
def orderItem(request, cart_id, product_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = int(form.cleaned_data['quantity'])
            total_price = quantity * float(product.discounted_price)
            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=total_price,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                payment_method=form.cleaned_data['payment_method'],
            )
            if order.payment_method == 'COD':
                cart.delete()
                messages.success(request, 'Order placed successfully!')
                return redirect('my-orders')
            elif order.payment_method == 'Card':
                return redirect(reverse('stripe_form') + f'?o_id={order.id}&c_id={cart.id}')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = OrderForm(initial={'email': request.user.email})

    return render(request, 'orderform.html', {'form': form, 'product': product})


@login_required
def myorders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myorders.html', {'orders': orders})


# ─── STRIPE ──────────────────────────────────────────────────────────────────

@login_required
def stripForm(request):
    order_id = request.GET.get('o_id')
    cart_id = request.GET.get('c_id')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    return render(request, 'strip_checkout.html', {'order': order, 'cart': cart})


@login_required
def create_checkout_session(request, order_id, cart_id):
    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Payment is not configured. Please contact support.')
        return redirect('cart')
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        cart = get_object_or_404(Cart, id=cart_id, user=request.user)
        domain = 'http://127.0.0.1:8000'
        unit_amount = int(float(order.total_price) * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'unit_amount': unit_amount,
                    'product_data': {
                        'name': f"{order.product.title} x{order.quantity}",
                        'description': order.product.s_description or '',
                    },
                },
                'quantity': 1,
            }],
            metadata={'order_id': order.id, 'cart_id': cart.id},
            mode='payment',
            success_url=domain + f'/success/?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}&cart_id={cart.id}',
            cancel_url=domain + '/cart',
        )
        return redirect(session.url, code=303)
    except stripe.error.AuthenticationError:
        messages.error(request, 'Stripe authentication failed. Please check API keys.')
        return redirect('cart')
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart')


def stripSuccess(request):
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')
    cart_id = request.GET.get('cart_id')

    if not session_id:
        messages.error(request, 'Invalid session.')
        return redirect('cart')
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            order = get_object_or_404(Order, id=order_id)
            order.payment_status = True
            order.order_status = 'In Progress'
            order.save()
            Cart.objects.filter(id=cart_id).delete()
            messages.success(request, 'Payment successful! Your order has been placed.')
            return redirect('my-orders')
        else:
            messages.warning(request, 'Payment not completed.')
            return redirect('cart')
    except stripe.error.StripeError as e:
        messages.error(request, f'Stripe error: {str(e)}')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart')


# ─── WISHLIST ────────────────────────────────────────────────────────────────

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    _, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.title} added to wishlist!')
    else:
        messages.info(request, 'Already in your wishlist.')
    return redirect('productdetails', product_id)


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': items})


@login_required
def remove_from_wishlist(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item.delete()
    messages.success(request, 'Removed from wishlist.')
    return redirect('wishlist')


# ─── PROFILE ─────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    completed = orders.filter(order_status='Complete').count()
    pending = orders.filter(order_status='In Progress').count()
    context = {
        'orders': orders[:5],
        'total_orders': orders.count(),
        'wishlist_count': wishlist_count,
        'completed': completed,
        'pending': pending,
    }
    return render(request, 'profile.html', context)


# ─── CHATBOT & SUPPORT ───────────────────────────────────────────────────────

def chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '').lower().strip()
            response = None
            for keyword, reply in CHATBOT_RESPONSES.items():
                if keyword in user_msg:
                    response = reply
                    break
            if not response:
                response = "I'm not sure about that. Please contact us at ashokkarki6677@gmail.com or call 9810549380."
            return JsonResponse({'reply': response})
        except Exception:
            return JsonResponse({'reply': 'Sorry, something went wrong. Please try again.'})
    return JsonResponse({'reply': 'Invalid request.'}, status=400)


def support_message(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False})


# ─── ERROR PAGES ─────────────────────────────────────────────────────────────

def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
