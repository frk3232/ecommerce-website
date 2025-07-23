from django.urls import path
from .import views

urlpatterns = [

    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('about/', views.about, name='about'),
    path('delcart/<int:id>', views.deletecart, name='delcart'),
    path('order/<int:cart_id>/', views.order_summary, name='order'),
    path('create-checkout-session/<int:cart_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('emtcart/', views.emptycart, name='emtcart'),
    path('registerform/', views.regform, name='registerform'),
    path('loginform/', views.logform, name='loginform'),
    path('loginout/', views.loginout, name='loginout'),
    path('success/', views.success, name='succes_page'),
    ]  