"""
Views for shop app.
"""

import math
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from shop.models import Category, Product , Cart, Checkout, OrderPlaced


class HomeView(LoginRequiredMixin, View):
    """
    Home page view.
    """
    def get(self, request):
        all_products = Product.objects.all().order_by('?')
        context = {
            'all_products': all_products
        }
        return render(request, 'index.html', context)


class AboutView(View):
    """
    About page view.
    """
    def get(self, request):
        return render(request, 'about.html')


class ShopView(LoginRequiredMixin, View):
    """
    Shop items view.
    """
    def get(self, request):
        all_products = Product.objects.all()
        
        """Pagination logic."""
        no_of_page = 3
        last = math.ceil(len(all_products)/int(no_of_page))
        page = request.GET.get('page')
        if(not str(page).isnumeric()):
            page = 1
        page = int(page)
        all_products = all_products[(page-1)*int(no_of_page): (page-1)*int(no_of_page)+int(no_of_page)]
        if (page==1):
            prev = '#'
            next = '/shop/items/?page='+ str(page+1)
        elif(page==last):
            prev = "/shop/items/?page=" + str(page - 1)
            next = "#"
        else:
            prev = "/shop/items/?page=" + str(page - 1)
            next = "/shop/items/?page=" + str(page + 1)

        context = {
            'all_products': all_products,
            'prev': prev,
            'next': next
        }

        return render(request, 'shop.html', context)


class SingleProductView(LoginRequiredMixin, View):
    """
    Single product view.
    """
    def get(self, request, product_slug):
        random_products = Product.objects.all().order_by('?')
        products = Product.objects.get(slug=product_slug)

        context = {
            'random_products': random_products,
            'products': products
        }

        return render(request, 'single-product.html', context)


class AddToCart(LoginRequiredMixin, View):
    """
    Products add into cart view.
    """
    def post(self, request, product_slug):
        auth_user = request.user       
        product = Product.objects.get(slug=product_slug)
        Cart(user=auth_user,product=product).save()

        return redirect('cart')


class CartVIew(LoginRequiredMixin, View):
    """
    Cart page view.
    """
    def get(self, request):
        auth_user = request.user
        cart_items = Cart.objects.filter(user=auth_user)

        carts = Cart.objects.all()
        cart = carts.filter(user=self.request.user).order_by('-id').distinct()

        amount = 0
        shipping = 45
        for i in cart:
            value = i.quantity * i.product.price
            amount = amount + value
        total = amount + shipping

        context = {
            'cart_items': cart_items,
            'shipping_amount': shipping,
            'cart_amount': amount,
            'total_amount': total
        }
        return render(request, 'cart.html', context)

    def remove_from_cart(request, cart_id):
        """Remove cart items."""
        cart = Cart.objects.get(id=cart_id)
        cart.delete()
        return redirect('cart')

    def update_quantity(request, cart_id):
        """Update cart quantity."""
        cart = Cart.objects.get(id=cart_id)
        cart.quantity += 1
        cart.save()
        return redirect('cart')

    def remove_quantity(request, cart_id):
        """Remove cart quantity."""
        cart = Cart.objects.get(id=cart_id)
        try:
            if cart.quantity == 1:
                pass
            else:
                cart.quantity -= 1
                cart.save()
        except Exception as e:
            print(e,'aaaaaa')

        return redirect('cart')
    

class CheckoutView(LoginRequiredMixin, View):
    """
    Checkout page view.
    """
    def get(self, request):
        carts = Cart.objects.all()
        cart = carts.filter(user=self.request.user).order_by('-id').distinct()

        amount = 0
        shipping = 45
        for i in cart:
            value = i.quantity * i.product.price
            amount = amount + value
        total = amount + shipping

        context = {
            'total_amount': total,
            'shipping_amount': shipping,
            'carts': cart,
            'sub_total': amount,
        }
        return render(request, 'checkout.html', context)
    

    def post(self, request):

        """
        Checkout bill address process.
        """
        auth_user = self.request.user
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        note = request.POST.get('bill')

        checkout = Checkout(
            user=auth_user, name=name, email=email, address=address, mobile=phone, note=note
            )
        
        """
        OrderPlaced Process.
        """
        cart = Cart.objects.filter(user=auth_user)
        for i in cart:
            OrderPlaced.objects.create(
                user=auth_user,product=i.product,quantity=i.quantity
            )
        checkout.save()
        cart.delete()

        return redirect('order')


class OrderView(LoginRequiredMixin, View):
    """Order view for users."""
    def get(self, request):
        order = OrderPlaced.objects.filter(user=self.request.user)

        amount = 0
        for i in order:
            if i.paid == False:    
                value = i.product.price * i.quantity
                amount = amount + value
    
        context = {
            'order': order,
            'total': amount
        }

        return render(request, 'order.html', context)


    """Delete user order."""
    def delete_order(request, product_id):
        prod = OrderPlaced.objects.get(id=product_id)
        prod.delete()
        return redirect('order')