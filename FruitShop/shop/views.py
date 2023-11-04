"""
Views for shop app.
"""

import math
from datetime import datetime
from django.db.models import Q
from django.contrib import messages
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from shop.models import (
    Category, Product , Cart, OrderPlaced, Coupon, Address
    )


class SearchView(View):
    """
    Search for users.
    """
    def get(self,request):
        """
        Search filter.
        """
        query = request.GET.get('q', '')  # Get the search query from the URL parameter
        results = Product.objects.filter(
            Q(title__icontains=query) | Q(category__title__icontains=query)
        )

        context = {
            'query': query,
            'results': results,
        }
        return render(request, 'search_results.html', context)


class HomeView(View):
    """
    Home page view.
    """
    def get(self, request):
        all_products = Product.objects.all()

        """Offer product."""
        prod_id = None
        for i in all_products:
            if i.is_time_limited:
                print(i.title)
                prod_id = i.id
                self.limited_time_product(prod_id)

        context = {
            'all_products': all_products,
            'offers': all_products,
        }
        return render(request, 'index.html', context)

    def limited_time_product(request,product_id):
        """Handle limited time products."""
        limited_prod = Product.objects.filter(id=product_id)
        current_date = datetime.now()
        for i in limited_prod:
            if i.is_time_limited:
                if current_date.strftime("%Y/%m/%d") >= i.date:
                    i.percent_off = None
                    i.is_time_limited = False
                    i.discount_price = None
                    i.date = None
                    i.save()


class AboutView(View):
    """
    About page view.
    """
    def get(self, request):
        return render(request, 'about.html')


class ContactUsView(View):
    """Contact page view."""
    def get(self, request):
        return render(request, 'contact.html')


class NewsView(View):
    """News page view."""
    def get(self, request):
        return render(request, 'news.html')


class ShopView(View):
    """
    Shop items view.
    """
    def get(self, request):
        all_products = Product.objects.all().order_by('-id')
        all_category = Category.objects.all().order_by('-id')

        """
        Pagination logic.
        """
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

        """
        Product show category vise.
        """
        allProds=[]
        catprods= Product.objects.values('category', 'id')

        cats= {item["category"] for item in catprods}
        for cat in cats:
            prod=Product.objects.filter(category=cat)
            n = len(prod)
            nSlides = n // 4 + math.ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])

        context = {
            'all_products': all_products,
            'all_category': all_category,
            'allProds': allProds,
            'prev': prev,
            'next': next,
        }

        return render(request, 'shop.html', context)

    """Listing separate items."""
    def get_separate_category_list(request, category_slug):

        category_slug_to_retrieve = category_slug
        all_category = Category.objects.all().order_by('-id')

        try:
            specific_category = Category.objects.get(slug=category_slug_to_retrieve)
        except Category.DoesNotExist:
            specific_category = None

        if specific_category:
            all_products = Product.objects.filter(category=specific_category)
            context = {
                'specific_category': specific_category,
                'all_products': all_products,
                'all_category': all_category,             
            }
        else:
            context = {
                'specific_category': None,
                'all_products': None,
                'all_category': None,
            }
        return render(request, 'separate_cat.html', context)


class SingleProductView(View):
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
        cart = Cart.objects.filter(user=auth_user, product=product).first()
        if cart:
            messages.info(request, "Already in ")
        else:        
            Cart(user=auth_user,product=product).save()
            return redirect('cart')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class CartVIew(LoginRequiredMixin, View):
    """
    Cart page view.
    """
    def get(self, request):
        auth_user = request.user
        cart_items = Cart.objects.filter(user=auth_user)

        amount = sum(self.calculate_item_total(item) for item in cart_items)
        shipping = 45
        discount_amount = request.session.get('discount_amount', 0)
        total = amount + shipping - discount_amount 
        request.session['total'] = total

        context = {
            'cart_items': cart_items,
            'shipping_amount': shipping,
            'cart_amount': amount,
            'total_amount': total,
        }
        return render(request, 'cart.html', context)

    def post(self, request):
        auth_user = request.user
        cart_items = Cart.objects.filter(user=auth_user)
        coupon_code = request.POST.get('coupon_code')        
        valid_coupon = Coupon.objects.filter(code=coupon_code, used=False).first()

        if valid_coupon:
            request.session['valid_coupon_code'] = valid_coupon.code
            request.session['discount_amount'] = valid_coupon.discount_value
            messages.success(request, 'Coupon applied!!')
        else:
            messages.warning(request, 'Invalid or already used coupon code.')

        return redirect('cart')

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

    def calculate_item_total(self, cart_item):
        if cart_item.product.is_time_limited:
            return cart_item.quantity * cart_item.product.discount_price
        else:
            return cart_item.quantity * cart_item.product.price


class CheckoutView(LoginRequiredMixin, View):
    """
    Checkout page view.
    """
    def get(self, request):
        carts = Cart.objects.all()
        address = Address.objects.filter(user=request.user)
        cart = carts.filter(user=self.request.user).order_by('-id').distinct()

        amount = 0
        shipping = 45
        for i in cart:
            if i.product.is_time_limited:
                value = i.quantity * i.product.discount_price
            else:
                value = i.quantity * i.product.price
            amount = amount + value
        
        if 'discount_amount' in request.session:
            total = amount + shipping - request.session['discount_amount']
            request.session['total'] = total
        else:
            total = amount + shipping

        context = {
            'address': address,
            'total_amount': total,
            'shipping_amount': shipping,
            'carts': cart,
            'sub_total': amount,
        }
        return render(request, 'checkout.html', context)
    

    def post(self, request):
        auth_user = self.request.user
        """
        OrderPlaced Process.
        """
        cart = Cart.objects.filter(user=auth_user)
        address_select = request.POST.get('selected_address')
        if address_select: 
            address = Address.objects.get(id=address_select)
        else:
            address = Address.objects.filter(user=auth_user).order_by('-default').first()

        for i in cart:
            if 'discount_amount' in request.session:
                OrderPlaced.objects.create(
                    user=auth_user, product=i.product, quantity=i.quantity, address=address,
                    price=request.session['total'], discount_price=request.session['discount_amount']
                )
            else:
                OrderPlaced.objects.create(
                    user=auth_user, product=i.product, quantity=i.quantity, address=address,
                    price=request.session['total']
                )

        if 'valid_coupon_code' in request.session:
            valid_coupon_code = request.session['valid_coupon_code']
            valid_coupon = Coupon.objects.filter(code=valid_coupon_code, used=False).first()
            if valid_coupon:
                valid_coupon.used = True
                valid_coupon.save()

            del request.session['total']
            del request.session['valid_coupon_code']
            del request.session['discount_amount']

        cart.delete()

        return redirect('order')


class OrderView(LoginRequiredMixin):
    """Order view for users."""
    def get_order(request):
        order = OrderPlaced.objects.filter(user=request.user)

        amount = 0
        for i in order:
            if i.paid == False:
                if i.product.is_time_limited:
                    value = i.product.discount_price * i.quantity
                else:
                    value = i.product.price * i.quantity
                amount = amount + value
    
        context = {
            'order': order,
            'total': amount
        }

        return render(request, 'order.html', context)

    """Get order details for authenticated users."""
    def get_order_details(request, order_id):
        auth_user = request.user
        order_details = get_object_or_404(OrderPlaced,user=auth_user,id=order_id)
        order = OrderPlaced.objects.filter(user=auth_user,id=order_id)

        shipping = 45
        amount = 0
        for i in order:
            if i.product.is_time_limited:
                value = i.product.discount_price * i.quantity
            else:
                value = i.product.price * i.quantity
            amount = amount + value
            
 
        discount = amount - order_details.price

        context = {
            'order':order_details,
            'amount': amount,
            'discount': discount,
            'shipping': shipping,
        }
        return render(request, 'order-detail.html', context)

    """Delete order for authenticated users."""
    def delete_order(request, order_id):
        order = OrderPlaced.objects.get(id=order_id)
        order.delete()
        return redirect('order')