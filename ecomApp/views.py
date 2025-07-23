from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, Cart
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'home.html')

@login_required
def products(request):
    products=Product.objects.all()
    return render(request, 'products.html', {'products':products})

@login_required
def cart(request):
    cart_item = list(Cart.objects.filter(user=request.user))
    for item in cart_item:
        item.total_price = item.quantity * item.product.price
    return render(request, 'cart.html', {'cart_item':cart_item})

@login_required
def add_to_cart(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    else:
        return redirect('login')

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def deletecart(request, id):
    item=Cart(id=id)
    item.delete()
    return redirect('cart')

@login_required
def emptycart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('cart')

@login_required
def order_summary(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    product_name = cart_item.product.name
    quantity = cart_item.quantity
    single_price = cart_item.product.price
    total_price = quantity * single_price

    context = {
        'product_name': product_name,
        'quantity': quantity,
        'single_price': single_price,
        'total_price': total_price,
        'grand_total': total_price,
        'cart_id': cart_id,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'order.html', context)


def regform(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('loginform')
    return render(request, 'registerform.html', {'form':form})

def logform(request):
    form=LoginForm(request,request.POST or None)
    if request.method=='POST' and form.is_valid():
        login(request,form.get_user())
        return redirect('products')
    return render(request, 'loginform.html', {'form':form})

@login_required
def loginout(request):
    logout(request)
    return redirect('home')

@login_required
@csrf_exempt
def create_checkout_session(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    product = cart_item.product
    quantity = cart_item.quantity
    unit_amount = int(product.price * 100)  

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def success(request):
    return render(request, 'success.html')