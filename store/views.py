from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import RegisterForm, ProductForm, UserProfileForm
from .models import UserProfile, Product, Order,Cart,CartItem
  
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            UserProfile.objects.create(user=user)  
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



@login_required
def panel_view(request):
    return render(request, 'panel.html')

def login_view(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=uname, password=pwd)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def home_view(request):
    recent_ids = request.session.get('recent', [])
    recent_products = Product.objects.filter(id__in=recent_ids)
    recent_products = sorted(recent_products, key=lambda x: recent_ids.index(x.id))
    return render(request, 'home.html', {'recent_products': recent_products})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_products(request):
    products = Product.objects.all().order_by('-id') 
    return render(request, 'admin_products.html', {'products': products})

@login_required
def products_view(request):
    products = Product.objects.all()
    return render(request,'product.html',{'products':products})


@login_required
def create_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('products_view')
    return render(request, 'create_product.html', {'form': form})

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('products_view')
    return render(request, 'update_product.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    recent = request.session.get('recent', [])
    if pk in recent:
        recent.remove(pk)
    recent.insert(0, pk)
    if len(recent) > 5:
        recent = recent[:5]
    request.session['recent'] = recent
    recent_products = Product.objects.filter(pk__in=recent).exclude(pk=pk)
    return render(request, 'product_detail.html', {
        'product': product,
        'recent_products': recent_products,
    })

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('products_view')

@login_required
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def update_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)  
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form})

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('view_cart')

# def view_cart(request):
#     cart = request.session.get('cart', {})
#     cart_items = []
#     total = 0
#     for product_id_str, quantity in cart.items():
#         product = get_object_or_404(Product, id=int(product_id_str))
#         item_total = product.price * quantity
#         total += item_total
#         cart_items.append({
#             'product': product,
#             'quantity': quantity,
#             'item_total': item_total,
#         })
#     return render(request, 'carts.html', {'cart_items': cart_items, 'total': total})

# def remove_from_cart(request, product_id):
#     cart = request.session.get('cart', {})
#     cart.pop(str(product_id), None)
#     request.session['cart'] = cart
#     return redirect('view_cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'admin_order_list.html', {'orders': orders})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = request.POST['status']
        order.save()
        return redirect('admin_order_list')
    return render(request, 'update_order_status.html', {'order': order})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin_order_list')
   
@login_required
def checkout(request):
    return render(request, 'checkout.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
    item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')
    total = cart.total()
    return render(request, 'carts.html', {'cart_items': items, 'total': total})

@login_required
def update_cart_item(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
        except ValueError:
            qty = 1  

        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()

    return redirect('view_cart')

@login_required
def remove_cart_item(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('view_cart')

@login_required
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return redirect('view_cart')























