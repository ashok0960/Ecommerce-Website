from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .access import vendor_only
from django.contrib.auth.models import User


@vendor_only
@login_required
def adminDashboard(request):
    from userpage.models import Order
    context = {
        'total_vendors': User.objects.filter(is_staff=True).count(),
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(order_status='In Progress').count(),
        'completed_orders': Order.objects.filter(order_status='Complete').count(),
        'recent_products': Product.objects.order_by('-created_at')[:10],
        'recent_orders': Order.objects.order_by('-created_at')[:10],
        'orders_to_manage': Order.objects.filter(order_status__in=['In Progress', 'way to deliver']).order_by('-created_at')[:20],
    }
    return render(request, 'admin/dashboard.html', context)


@vendor_only
@login_required
def vendorDashboard(request):
    from userpage.models import Order
    products = Product.objects.filter(user=request.user)

    # Get orders for products uploaded by this vendor
    vendor_product_ids = products.values_list('id', flat=True)
    vendor_orders = Order.objects.filter(product_id__in=vendor_product_ids).order_by('-created_at')

    context = {
        'total_products': products.count(),
        'total_categories': Category.objects.filter(user=request.user).count(),
        'low_stock': products.filter(stock__gt=0, stock__lte=5).count(),
        'out_of_stock': products.filter(stock=0).count(),
        'trending_products': products.filter(trending=True).count(),
        'recent_products': products.order_by('-created_at')[:6],
        'vendor_orders': vendor_orders.filter(order_status__in=['In Progress', 'way to deliver'])[:10],
        'total_vendor_orders': vendor_orders.count(),
        'pending_vendor_orders': vendor_orders.filter(order_status='In Progress').count(),
        'completed_vendor_orders': vendor_orders.filter(order_status='Complete').count(),
    }
    return render(request, 'vendor/dashboard.html', context)


@vendor_only
@login_required
def addCategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request,'Category Added')
            return redirect('all-category')
        else:
            messages.error(request,'Invalid Input')
            return render(request,'vendor/addcategory.html', {'form':form})
    context = {'form': CategoryForm}
    return render(request,'vendor/addcategory.html', context)

@vendor_only
@login_required
def allCategory(request):
    context = {
        'categories' : Category.objects.filter(user=request.user)
    }
    return render(request,'vendor/allcategory.html',context)

@vendor_only
@login_required
def deleteCategory(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category Deleted Successfully.')
    return redirect('all-category')

@vendor_only
@login_required
def updateCategory(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'Category Updated Successfully.')
            return redirect('all-category')
    context = {'form': CategoryForm(instance=category)}
    return render(request,'vendor/updatecategory.html',context)

@vendor_only
@login_required
def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request,'Product Added successfully.')
            return redirect('all-products')
        else:
            messages.error(request,'Product Add Failed.')
            return render(request,'vendor/addProduct.html', {'form':form})
    context = {'form': ProductForm}
    return render(request,'vendor/addProduct.html', context)

@vendor_only
@login_required
def allProducts(request):
    context = {
        'products' : Product.objects.filter(user=request.user)
    }
    return render(request,'vendor/allproducts.html',context)

@vendor_only
@login_required
def deleteProduct(request, product_id):
    product = Product.objects.get(id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product Deleted Successfully.')
    return redirect('all-products')

@vendor_only
@login_required
def updateProduct(request, product_id):
    product = Product.objects.get(id=product_id, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,'Product Updated Successfully.')
            return redirect('all-products')
    context = {'form': ProductForm(instance=product)}
    return render(request,'vendor/updateproduct.html',context)


# Order Management Views
@login_required
def update_order_status(request, order_id):
    from userpage.models import Order
    from django.contrib import messages

    try:
        order = Order.objects.get(id=order_id)

        # Check permissions
        if request.user.is_superuser:
            # Admin can update any order
            pass
        elif request.user.is_staff and order.product.user == request.user:
            # Vendor can only update orders for their own products
            pass
        else:
            messages.error(request, 'You do not have permission to update this order.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        if request.method == 'POST':
            new_status = request.POST.get('order_status')
            if new_status in ['In Progress', 'way to deliver', 'Complete']:
                order.order_status = new_status
                order.save()
                messages.success(request, f'Order status updated to {new_status}')
            else:
                messages.error(request, 'Invalid status selected')

        return redirect(request.META.get('HTTP_REFERER', 'home'))

    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    except Exception as e:
        messages.error(request, f'Error updating order: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def manage_orders(request):
    from userpage.models import Order

    if request.user.is_superuser:
        # Admin can see all orders
        orders = Order.objects.all().order_by('-created_at')
        title = "All Orders Management"
    elif request.user.is_staff:
        # Vendor can only see orders for their products
        vendor_products = Product.objects.filter(user=request.user).values_list('id', flat=True)
        orders = Order.objects.filter(product_id__in=vendor_products).order_by('-created_at')
        title = "My Product Orders"
    else:
        messages.error(request, 'Access denied')
        return redirect('home')

    # Handle status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        orders = orders.filter(order_status=status_filter)

    context = {
        'orders': orders,
        'title': title,
        'status_filter': status_filter,
        'is_admin': request.user.is_superuser,
        'is_vendor': request.user.is_staff and not request.user.is_superuser,
    }
    return render(request, 'manage_orders.html', context)