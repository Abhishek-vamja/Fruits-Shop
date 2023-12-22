"""
Views for the shop app.

This module contains view classes that handle various aspects of the online shop application, including product browsing,
shopping cart management, order placement, and user interaction. These views leverage Django's class-based views for
flexibility and code organization. The views are structured to enhance user experience and simplify the online shopping process.

Classes:
- ShopView(View): Manages the display of product listings and category filtering.
- AddToCart(LoginRequiredMixin, View): Handles adding products to the shopping cart.
- CheckoutView(LoginRequiredMixin, View): Manages the checkout process and order placement.
- OrderView(LoginRequiredMixin, View): Displays user orders and order details.
- SingleProductView(View): Renders a single product's details page.
- AboutView(View): Displays information about the online shop.
- HomeView(View): Represents the homepage of the shop app, highlighting featured and limited-time offers.
- SearchView(View): Allows users to search for products based on keywords and categories.
"""

import math
import razorpay
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.views.generic import View
from django.http import HttpResponseRedirect
from user.views import get_time_of_day_greeting
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from shop.models import (
    Category, Product, Cart, OrderPlaced, Coupon, Address, Contact, News, Comment, Quote
)


class SearchView(View):
    """
    Search view for users.

    This class represents the search view for the website, allowing users to search for products based on keywords and
    categories. It provides a simple search filter to retrieve relevant search results from the product database.
    """


    def get(self,request):
        """
        Handle user search queries and display search results.

        This method processes user search queries by retrieving the search query from the URL parameter and filtering the
        product database to find products that match the query. It provides the search results to the user.
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

    This class represents the primary view for the website's home page. It is responsible for displaying a collection of
    products to users, including any limited-time offers. It also includes logic for managing limited-time product
    promotions.
    """


    def get(self, request):
        """
        Render the home page with a list of available products and time-limited offers.

        This method retrieves all available products and time-limited offers, providing users with an overview of the
        products available on the website's home page. It also handles limited-time product promotions and updates product
        details as needed.
        """
        all_products = Product.objects.all().order_by('?')
        all_news = News.objects.all().order_by('-created_at')[:3]
        all_quotes = Quote.objects.all().order_by('?')[:3]
        
        # Offer product
        prod_id = None
        for i in all_products:
            if i.is_time_limited:
                print(i.title)
                prod_id = i.id
                self.limited_time_product(prod_id)

        context = {
            'all_products': all_products,
            'offers': all_products,
            'all_news': all_news,
            'all_quotes': all_quotes,
        }
        return render(request, 'index.html', context)

    def limited_time_product(request,product_id):
        """
        Handle time-limited product promotions and update product details.

        This method is responsible for managing time-limited product promotions. It checks the current date and compares it
        to the end date of a time-limited product. If the end date has passed, the method updates the product details to
        remove the time-limited offer.
        """
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

    This class represents a view dedicated to displaying information about a website, organization, or individual. It serves
    as a simple way to inform users about the purpose, history, or background of the website, helping to build trust and
    transparency.
    """


    def get(self, request):
        """
        Render the 'About Us' page, providing users with valuable information.

        This method renders the 'About Us' page, offering users insights into the background, mission, or history of the website,
        organization, or individual. It plays a significant role in building trust and transparency with the users.
        """
        return render(request, 'about.html')


class ContactUsView(View):
    """Contact page view."""


    def get(self, request):
        return render(request, 'contact.html')

    def post(self, request):
        user = request.user
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact_obj = Contact(
            user=user, name=name, email=email, phone=phone,
            subject=subject, message=message
        )

        contact_obj.save()
        return redirect('contact-us')


class NewsView(View):
    """News page view."""


    def get(self, request):
        news_obj = News.objects.all()
        context = {
            'news': news_obj
        }
        return render(request, 'news.html', context)

    class SingleNewsView(View):
        """Single news view."""

        def get(self, request, news_id):
            news_obj = News.objects.get(id=news_id)
            comment_obj = Comment.objects.filter(news=news_id)[:5]
            recent_posts = News.objects.all()[:5]

            context = {
                'news': news_obj,
                'comments': comment_obj,
                'recent_posts': recent_posts
            }
            return render(request, 'single-news.html', context)

        def post(self, request, news_id):
            user = request.user
            news_obj = get_object_or_404(News, id=news_id)
            message = request.POST.get('comment')

            comment_obj = Comment.objects.create(
                user=user, news=news_obj, message=message
            )
            
            comment_obj.save()
            return redirect('single-news', news_id=news_id)


class ShopView(View):
    """
    Shop items view.

    This class provides a view for displaying a list of shop items, including pagination for browsing through items, and the ability
    to view items of a specific category.
    """


    def get(self, request):
        """
        Render the shop page with a list of items, including pagination and product categorization.

        This method retrieves a list of all available products, applies pagination logic to divide them into multiple pages,
        and displays the products with the ability to navigate between pages. It also categorizes and displays products based
        on their respective categories.
        """
        all_products = Product.objects.all().order_by('-id')
        all_category = Category.objects.all().order_by('-id')
  
        # Pagination logic.
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

        
        # Product show category vise.
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

    def get_separate_category_list(request, category_slug):
        """
        Retrieve and display items of a specific category.

        This method retrieves and displays a list of products belonging to a specific category identified by its unique slug.
        """
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

    This class provides a view for displaying detailed information about a single product, along with a selection of random
    products to suggest to the user.
    """


    def get(self, request, product_slug):
        """
        Render the single product page with product details and random product suggestions.

        This method retrieves the details of a single product specified by its unique slug and gathers a list of random products
        to suggest to the user. It then renders the single-product page with these details.
        """
        random_products = Product.objects.all().order_by('?')
        products = Product.objects.get(slug=product_slug) 
        get_greeting = get_time_of_day_greeting()
        print(get_greeting)

        context = {
            'random_products': random_products,
            'greeting': get_greeting,
            'products': products
        }

        return render(request, 'single-product.html', context)


class AddToCart(LoginRequiredMixin, View):
    """
    Products add into cart view.

    This class provides views for adding products to the user's shopping cart.
    """


    def post(self, request, product_slug):
        """
        Handle the addition of a product to the shopping cart.

        This method allows authenticated users to add a product to their shopping cart. It checks if the product is already in
        the cart and provides appropriate feedback to the user. If the product is not in the cart, it adds it and redirects to
        the cart page.
        """
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

    This class provides views for managing the user's shopping cart.
    """


    def get(self, request):
        """
        Display the user's cart.
        This method retrieves and displays the items in the user's shopping cart, including the total and shipping costs.
        """
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
        """
        Apply a coupon to the cart.
        This method allows users to apply a coupon code to receive a discount on their cart total.
        """
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
        """
        Remove an item from the cart.
        This method allows users to remove a specific item from their shopping cart.
        """
        cart = Cart.objects.get(id=cart_id)
        cart.delete()
        return redirect('cart')

    def update_quantity(request, cart_id):
        """
        Update the quantity of an item in the cart.
        This method allows users to increase the quantity of a specific item in their cart.
        """
        cart = Cart.objects.get(id=cart_id)
        cart.quantity += 1
        cart.save()
        return redirect('cart')

    def remove_quantity(request, cart_id):
        """
        Reduce the quantity of an item in the cart.
        This method allows users to decrease the quantity of a specific item in their cart, down to a minimum of 1.
        """
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
        """
        Calculate the total cost of an item in the cart.
        This method calculates the total cost of a specific item in the cart based on its quantity and price.
        """
        if cart_item.product.is_time_limited:
            return cart_item.quantity * cart_item.product.discount_price
        else:
            return cart_item.quantity * cart_item.product.price


class CheckoutView(LoginRequiredMixin, View):
    """
    Checkout page view.

    This class provides views for the checkout process, including rendering the checkout page with cart contents,
    address selection, order placement, and handling discounts.
    """

    def get(self, request):
        """
        Render the checkout page.

        This method handles the rendering of the checkout page, including the user's shopping cart contents, available delivery
        addresses, and order total calculations. It also accounts for discounts and shipping charges, providing a comprehensive
        overview for the user during the checkout process.
        """
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
        """
        Process an order and complete the checkout.

        This method handles the order placement process when a user proceeds to checkout. It retrieves the user's cart items,
        validates the selected or default address, creates order entries, applies discounts if available, clears the cart, and 
        redirects the user to the order confirmation page.
        """
        auth_user = self.request.user

        # OrderPlaced Process
        cart = Cart.objects.filter(user=auth_user)
        address_select = request.POST.get('selected_address')

        if address_select: 
            address = Address.objects.get(id=address_select)
        else:
            address = Address.objects.filter(user=auth_user).order_by('-default').first()

        if address is None:
            messages.warning(request, 'Please select or add an address!!')
            return redirect('checkout')

        if 'discount_amount' in request.session:               
            order = OrderPlaced.objects.create(
                user=auth_user, address=address,
                price=request.session['total'], discount_price=request.session['discount_amount']
            )
        else:   
            order = OrderPlaced.objects.create(
                user=auth_user, address=address,
                price=request.session['total']
            )

        for i in cart:
            order.product.add(i.product)

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
    """
    Order view for authenticated users.

    This class provides views for viewing, retrieving details, and deleting orders placed by the authenticated users.
    """
    
    def get_order(request):
        """
        Render the user's orders.
        This method retrieves and renders a list of orders placed by the authenticated user,
        including total order amounts.
        """
        orders = OrderPlaced.objects.filter(user=request.user)
        total_amount = 0

        for order in orders:
            order_amount = 0
            for product in order.product.all():
                if not order.paid:
                    if product.is_time_limited:
                        order_amount += product.discount_price * order.quantity
                    else:
                        order_amount += product.price * order.quantity

            total_amount += order_amount

        context = {
            'order': orders,
            'total': total_amount
        }
        return render(request, 'order.html', context)

    def get_order_details(request, order_id):
        """
        Retrieve and render order details.
        This method retrieves and renders detailed information about a specific order placed by the authenticated user.
        It includes the total amount, discounts, and shipping costs.
        """

        auth_user = request.user
        order_details = OrderPlaced.objects.filter(user=auth_user,id=order_id)
        user_orders = OrderPlaced.objects.get(user=auth_user,id=order_id)

        shipping = 45
        amount = 0

        for order_item in order_details:
            for i in order_item.product.all():
                if i.is_time_limited:
                    value = i.discount_price * order_item.quantity
                else:
                    value = i.price * order_item.quantity
                amount += value

            discount = amount - order_item.price

        context = {
            'order': user_orders,
            'amount': amount,
            'discount': discount,
            'shipping': shipping,
        }
        return render(request, 'order-detail.html', context)

    def delete_order(request, order_id):
        """
        Delete a user's order.
        This method allows authenticated users to delete a specific order placed by them.
        """
        order = OrderPlaced.objects.get(id=order_id)
        order.delete()
        return redirect('order')
