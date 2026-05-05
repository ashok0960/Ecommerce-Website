from django.shortcuts import render, redirect, get_object_or_404
from product.models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import*
from django.contrib import messages
from .forms import *
from django.urls import reverse
import stripe
from django.conf import settings

# Configure Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
    context = {
        'products': Product.objects.filter(trending=True).order_by('-id')[:4]
    }
    return render(request,'index.html', context)

def about(request):
    return render(request,'about.html')

def products(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    search_query = request.GET.get('search')

    products = Product.objects.all().order_by('-id')

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(l_description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': int(category_id) if category_id else None,
        'search_query': search_query
    }

    return render(request, 'products.html', context)


def productDetails(request,product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'item': product
    }
    return render(request,'product_details.html',context)


@login_required
def addtocart(request,product_id):
    product= Product.objects.get(id = product_id)
    user = request.user
    existingItem = Cart.objects.filter(user=user, product=product)
    if existingItem:
        messages.error(request, "Item Already Exist")
        return redirect('productdetails',product_id)
    else:
        Cart.objects.create(user=user, product=product)
        messages.success(request, "Items added to the cart")
        return redirect("cart")
    
@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user)
    context={
        "cartitems": cart
    }
    return render(request,'allcarts.html',context)


def delete_cart(request,cart_id):
    cart= Cart.objects.get(id=cart_id)
    cart.delete()
    messages.success(request, "Item Deleted Successfully!")
    return redirect('cart')

@login_required
def orderItem(request,cart_id,product_id):
    cart=Cart.objects.get(id=cart_id)
    product = Product.objects.get(id=product_id)
    user = request.user

    if request.method =='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            quantity = request.POST.get('quantity')
            price = product.discounted_price
            address = request.POST.get('address')
            total_price = int(quantity) * int(price)
            phone=request.POST.get('phone')
            email=request.POST.get('email')
            address=request.POST.get('address')
            payment_method=request.POST.get('payment_method')

            order =Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                total_price=total_price,
                address=address,
                phone=phone,
                email=email,
                payment_method=payment_method


            )
            if order.payment_method == "COD":
                cart = Cart.objects.get(id = cart_id)
                cart.delete()
                messages.success(request,'Order Placed Successfull')
                return redirect('home')
            

            elif order.payment_method == 'Card':
                return redirect(reverse('stripe_form')+'?o_id='+str(order.id)+'&c_id='+str(cart.id))
            
            else:
                messages.error(request,'Order Placed UnSuccessfull')
                return redirect('home')
        
    


    
    context={
        'form': OrderForm

    }
    return render(request,'orderform.html',context)


@login_required
def stripForm(request):
    cart_id = request.GET.get('c_id')
    order_id = request.GET.get('o_id')
    order = get_object_or_404(Order, id=order_id)
    cart = Cart.objects.get(id=cart_id)
    context = {
        'order': order,
        'cart': cart
    }
    return render(request, 'strip_checkout.html', context)

@login_required
def create_checkout_session(request, order_id, cart_id):
    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Stripe is not configured. Please contact support.')
        return redirect('cart')
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        cart = get_object_or_404(Cart, id=cart_id, user=request.user)
        YOUR_DOMAIN = 'http://127.0.0.1:8000'

        # unit_amount = total_price in cents (already includes quantity)
        unit_amount = int(float(order.total_price) * 100)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'unit_amount': unit_amount,
                        'product_data': {
                            'name': f"{order.product.title} x{order.quantity}",
                            'description': order.product.s_description or '',
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'order_id': order.id,
                'cart_id': cart.id,
                'user_id': request.user.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + f'/success/?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}&cart_id={cart.id}',
            cancel_url=YOUR_DOMAIN + '/cart',
        )
        return redirect(checkout_session.url, code=303)
    except stripe.error.AuthenticationError:
        messages.error(request, 'Stripe authentication failed. Please check your API keys.')
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
        messages.error(request, 'Invalid Session.')
        return redirect('cart')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            order = Order.objects.get(id=order_id)
            cart = Cart.objects.get(id=cart_id)
            order.payment_status = True
            order.order_status = 'In Progress'
            order.save()
            cart.delete()

            messages.success(request, 'Payment successful! Your order has been placed.')
            return redirect('home')
        else:
            messages.warning(request, 'Payment not completed.')
            return redirect('cart')
    except stripe.error.StripeError as e:
        messages.error(request, f'Stripe error: {str(e)}')
        return redirect('cart')
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('cart')
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found.')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart')
    



@login_required
def myorders(request):
    order = Order.objects.filter(user=request.user)
    context={
        'orders': order
    }
    return render(request,'myorders.html',context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['ashokkarki6677@gmail.com'],
                    fail_silently=False,
                )
            except Exception:
                pass
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    context = {
        'form': form
    }
    return render(request, 'contact.html', context) 


from django.http import JsonResponse

def support_message(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False})

 
