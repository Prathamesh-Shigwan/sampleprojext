import json
import logging
from decimal import Decimal
from venv import logger

from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import razorpay
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .models import *
from .forms import *

client = razorpay.Client(auth=("rzp_test_KNDTUWOZLejvQp", "BlKrxZkEyxkyC0SWUjC2ZNIV"))

def home(request):
    products = Product.objects.filter(product_status="published", featured=True).order_by('-id')
    main_categories = MainCategory.objects.prefetch_related('subcategories').all().order_by('-id')[:9]
    color_choices = {color[0]: color[1] for color in ProductVariant.COLOR_CHOICES}

    context = {
        'products': products,
        'main_categories': main_categories,
        'color_choices': color_choices,
    }
    return render(request, 'home.html', context)

def cart_view(request):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in to view your cart.", status=403)

    cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'total': Decimal('0.00')})
    if cart.discount_code:
        cart.apply_discount()

    items = CartItem.objects.filter(cart=cart)

    try:
        shipping = SiteSettings.objects.first().shipping_charge
    except (SiteSettings.DoesNotExist, AttributeError):
        shipping = Decimal('0.00')

    final_total = cart.total + shipping

    context = {
        'cart': cart,
        'items': items,
        'total': cart.total,
        'final_total': final_total,
        'shipping': shipping,
    }
    return render(request, 'cart.html', context)

def contact(request):
    success_message = None  # Initialize the success message variable
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']  # Sender's email
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            email_subject = f"Contact Form Submission from {name}: {subject}"
            email_message = f"Message from {email}:\n\n{message}"

            try:
                send_mail(
                    email_subject,
                    email_message,
                    email,  # From email (sender's email)
                    ['prathameshshigwan52@gmail.com'],  # To email (your email or business email)
                    fail_silently=False,
                )
                success_message = "Your message has been sent successfully. Thank you for contacting us!"
            except Exception as e:
                success_message = "An error occurred while sending your message. Please try again."

    else:
        form = ContactForm()

    return render(request, 'contact.html', {
        'form': form,
        'success_message': success_message
    })

def base(request, cid=None, is_subcategory=False):
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    page = request.GET.get('page', 1)
    products = Product.objects.filter(product_status="published", featured=True).order_by('-id')

    if cid:
        if is_subcategory:
            category = get_object_or_404(SubCategory, sid=cid)
            products = products.filter(sub_category=category)
        else:
            category = get_object_or_404(MainCategory, cid=cid)
            products = products.filter(main_category=category)

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    if color:
        products = products.filter(variants__color=color)

    main_categories = MainCategory.objects.all().order_by('-id')
    sub_categories = SubCategory.objects.all().order_by('-id')

    paginator = Paginator(products, 10)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    color_choices = {color[0]: color[1] for color in ProductVariant.COLOR_CHOICES}

    context = {
        'products': products_page,
        'main_categories': main_categories,
        'sub_categories': sub_categories,
        'color_choices': color_choices,
    }
    return render(request, 'base.html', context)

def product_grid(request, cid=None, is_subcategory=False):
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    gender = request.GET.get('gender')
    page = request.GET.get('page', 1)
    products = Product.objects.filter(product_status="published").order_by('-id')

    if cid:
        if is_subcategory:
            category = get_object_or_404(SubCategory, sid=cid)
            products = products.filter(sub_category=category)
        else:
            category = get_object_or_404(MainCategory, cid=cid)
            products = products.filter(main_category=category)

    if gender:
        gender_list = gender.split(',')
        products = products.filter(variants__gender__in=gender_list).distinct()

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    if color:
        products = products.filter(variants__color=color).distinct()

    main_categories = MainCategory.objects.all().order_by('-id')
    sub_categories = SubCategory.objects.all().order_by('-id')

    paginator = Paginator(products, 10)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    color_choices = {color[0]: color[1] for color in ProductVariant.COLOR_CHOICES}

    context = {
        'products': products_page,
        'main_categories': main_categories,
        'sub_categories': sub_categories,
        'color_choices': color_choices.items(),
    }
    print(f"Products: {products_page}")  # Debugging line
    return render(request, 'product-grid.html', context)

def product_list(request):
    page = request.GET.get('page', 1)
    products = Product.objects.filter(product_status="published", featured=True).order_by('-id')

    paginator = Paginator(products, 10)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        'products': products_page,
    }
    return render(request, 'product-list.html', context)

def product_details(request, pid):
    products = Product.objects.filter(product_status="published", featured=True).order_by('-id')
    product = get_object_or_404(Product, pid=pid)
    images = ExtraImages.objects.filter(product=product)
    context = {
        'product': product,
        'products': products,
        'images': images,
    }
    return render(request, 'product-details.html', context)

def wishlist(request):
    try:
        wishlist = Wishlist.objects.all()
    except:
        wishlist = None

    context = {"w": wishlist}
    return render(request, 'wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request):
    product_id = request.POST.get('id')
    user = request.user

    try:
        product = Product.objects.get(id=product_id)
        if Wishlist.objects.filter(product=product, user=user).exists():
            return JsonResponse({"bool": False, "message": "Product already in wishlist"})
        else:
            Wishlist.objects.create(product=product, user=user)
            return JsonResponse({"bool": True, "message": "Product added to wishlist"})
    except Product.DoesNotExist:
        return JsonResponse({"bool": False, "message": "Product not found"})

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def add_to_cart(request, pid):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)

    product = get_object_or_404(Product, pid=pid)
    cart, created = Cart.objects.get_or_create(user=request.user, defaults={'total': 0})

    requested_quantity = int(request.POST.get('quantity', 1))
    if product.inventory.stock_quantity < requested_quantity:
        return JsonResponse({"success": False, "error": "Insufficient stock available"}, status=400)

    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        cart=cart,
        defaults={'quantity': requested_quantity, 'line_total': product.price * requested_quantity}
    )

    if not created:
        if cart_item.quantity + requested_quantity > product.inventory.stock_quantity:
            return JsonResponse({"success": False, "error": "Insufficient stock available"}, status=400)
        cart_item.quantity += requested_quantity
        cart_item.line_total = cart_item.quantity * product.price
        cart_item.save()

    cart.total = sum(item.line_total for item in cart.cartitem_set.all())
    cart.save()

    return JsonResponse({"success": True, "total_items": cart.cartitem_set.count(), "cart_total": cart.total})

def remove_from_cart(request, item_id):
    try:
        if request.user.is_authenticated:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            messages.success(request, "Item removed from cart.")
        else:
            messages.error(request, "You need to be logged in to remove items from the cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in cart.")

    return redirect('products:cart_view')

@require_POST
def update_cart_item(request):
    data = json.loads(request.body)
    item_id = data['item_id']
    quantity = int(data['quantity'])

    cart_item = CartItem.objects.get(id=item_id)
    cart_item.quantity = quantity
    cart_item.line_total = cart_item.product.price * Decimal(quantity)
    cart_item.save()

    cart = cart_item.cart
    cart.total = sum(item.line_total for item in CartItem.objects.filter(cart=cart))
    cart.save()

    try:
        shipping = SiteSettings.objects.first().shipping_charge
    except AttributeError:
        shipping = Decimal('0.00')

    final_total = cart.total + shipping

    return JsonResponse({
        'success': True,
        'new_line_total': float(cart_item.line_total),
        'cart_total': float(cart.total),
        'shipping': float(shipping),
        'final_total': float(final_total)
    })

@login_required
def save_info(request):
    try:
        billing_address = BillingAddress.objects.filter(user=request.user).first()
        shipping_address = ShippingAddress.objects.filter(user=request.user).first()

        if request.method == 'POST':
            billing_form = BillingForm(request.POST, instance=billing_address)
            shipping_form = ShippingForm(request.POST, instance=shipping_address)

            if billing_form.is_valid() and shipping_form.is_valid():
                saved_billing = billing_form.save(commit=False)
                saved_billing.user = request.user
                saved_billing.save()

                saved_shipping = shipping_form.save(commit=False)
                saved_shipping.user = request.user
                saved_shipping.save()

                messages.success(request, "Billing and shipping information saved successfully.")
                return redirect('products:checkout')
            else:
                messages.error(request, "There was an error saving your information. Please try again.")
        else:
            billing_form = BillingForm(instance=billing_address)
            shipping_form = ShippingForm(instance=shipping_address)

        context = {
            'billing_form': billing_form,
            'shipping_form': shipping_form,
        }
        return render(request, 'checkout.html', context)
    except Exception as e:
        logger.error(f"Error in save_info process: {e}")
        messages.error(request, 'Error accessing the save info page. Please try again.')
        return redirect('home')

@login_required
@csrf_protect
def save_info(request):
    billing_address = BillingAddress.objects.filter(user=request.user).first()
    shipping_address = ShippingAddress.objects.filter(user=request.user).first()

    if request.method == 'POST':
        billing_form = BillingForm(request.POST, instance=billing_address)
        shipping_form = ShippingForm(request.POST, instance=shipping_address)

        if billing_form.is_valid() and shipping_form.is_valid():
            saved_billing = billing_form.save(commit=False)
            saved_billing.user = request.user
            saved_billing.save()

            saved_shipping = shipping_form.save(commit=False)
            saved_shipping.user = request.user
            saved_shipping.save()

            messages.success(request, "Billing and shipping information saved successfully.")
        else:
            messages.error(request, "There was an error saving your information. Please try again.")

    return redirect('products:checkout')

@login_required
@csrf_protect
def checkout(request):
    try:
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'total': Decimal('0.00')})
        items = CartItem.objects.filter(cart=cart)

        if not items.exists():
            messages.error(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
            return redirect('products:cart_view')

        billing_address = BillingAddress.objects.filter(user=request.user).first()
        shipping_address = ShippingAddress.objects.filter(user=request.user).first()

        if request.method == 'POST' and 'process_payment' in request.POST:
            try:
                shipping = SiteSettings.objects.first().shipping_charge if SiteSettings.objects.exists() else Decimal('0.00')
                final_total = float(cart.total) + float(shipping)

                amount = final_total * 100
                razorpay_order = client.order.create({
                    "amount": amount,
                    "currency": "INR",
                    "payment_capture": "1"
                })

                razorpay_order_id = razorpay_order['id']

                request.session['razorpay_order_id'] = razorpay_order_id
                request.session['amount'] = amount

                context = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                    'currency': 'INR',
                    'amount': amount,
                    'billing_address': billing_address,
                    'shipping_address': shipping_address,
                    'callback_url': reverse('products:process_order'),
                }
                return render(request, 'payment.html', context)
            except Exception as e:
                logger.error(f"Exception during Razorpay order creation: {e}")
                messages.error(request, "An error occurred during the payment process. Please try again.")
                return redirect('products:checkout')

        else:
            billing_form = BillingForm(instance=billing_address)
            shipping_form = ShippingForm(instance=shipping_address)

        shipping = SiteSettings.objects.first().shipping_charge if SiteSettings.objects.exists() else Decimal('0.00')
        final_total = float(cart.total) + float(shipping)

        context = {
            'cart': cart,
            'items': items,
            'total': float(cart.total),
            'final_total': final_total,
            'shipping': float(shipping),
            'billing_form': billing_form,
            'shipping_form': shipping_form,
        }
        return render(request, 'checkout.html', context)
    except Exception as e:
        logger.error(f"Error in checkout process: {e}")
        messages.error(request, 'Error accessing the checkout page. Please try again.')
        return redirect('home')

@login_required
@csrf_protect
def process_order(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        if not payment_id or not razorpay_order_id or not signature:
            messages.error(request, "Payment was canceled.")
            return redirect('products:cart_view')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            payment_details = client.payment.fetch(payment_id)
            payment_method = payment_details['method']

            user = request.user

            cart = Cart.objects.get(user=user)
            billing_address = BillingAddress.objects.filter(user=user).first()
            shipping_address = ShippingAddress.objects.filter(user=user).first()

            if not user.first_name or not user.last_name:
                messages.error(request, "User information is incomplete. Please update your profile.")
                return redirect('accounts:profile_update')

            with transaction.atomic():
                items = CartItem.objects.filter(cart=cart)
                for item in items:
                    if item.quantity > item.product.inventory.stock_quantity:
                        messages.error(request, f"Insufficient stock for {item.product.name}.")
                        return redirect('products:cart_view')

                order = Order.objects.create(
                    user=user,
                    billing_full_name=billing_address.billing_full_name,
                    billing_email=billing_address.billing_email,
                    billing_address1=billing_address.billing_address1,
                    billing_address2=billing_address.billing_address2,
                    billing_city=billing_address.billing_city,
                    billing_state=billing_address.billing_state,
                    billing_zipcode=billing_address.billing_zipcode,
                    billing_country=billing_address.billing_country,
                    billing_phone=billing_address.billing_phone,
                    shipping_full_name=shipping_address.shipping_full_name,
                    shipping_email=shipping_address.shipping_email,
                    shipping_address1=shipping_address.shipping_address1,
                    shipping_address2=shipping_address.shipping_address2,
                    shipping_city=shipping_address.shipping_city,
                    shipping_state=shipping_address.shipping_state,
                    shipping_zipcode=shipping_address.shipping_zipcode,
                    shipping_country=shipping_address.shipping_country,
                    shipping_phone=shipping_address.shipping_phone,
                    total=cart.total,
                    payment_method=payment_method
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        user=user,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    item.product.inventory.stock_quantity -= item.quantity
                    item.product.inventory.save()
                    item.delete()

                cart.total = Decimal('0.00')
                cart.save()
                send_order_email(request, order.id)

            messages.success(request, "Your order has been placed successfully.")
            return redirect('products:order_tracking')

        except razorpay.errors.SignatureVerificationError as e:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('products:cart_view')
        except Exception as e:
            messages.error(request, "An error occurred during the payment process. Please try again.")
            return redirect('products:cart_view')
    else:
        return redirect('home')

@login_required
def send_order_email(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    billing_address = BillingAddress.objects.filter(user=request.user).first()
    shipping_address = BillingAddress.objects.filter(user=request.user).first()

    site_settings = SiteSettings.objects.first()
    shipping_charge = site_settings.shipping_charge if site_settings else Decimal('0.00')
    final_total = order.total + shipping_charge

    subject = f"DBMS Order Confirmation - Order #{order.id}"
    html_content = render_to_string('order_email.html', {
        'order': order,
        'items': items,
        'billing_address': billing_address,
        'shipping_address': shipping_address,
        'shipping_charge': shipping_charge,
        'final_total': final_total,
        'user': request.user
    })
    text_content = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = ['prathameshshigwan222@gmail.com', request.user.email]

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

    return JsonResponse({'success': True, 'message': 'Email sent successfully'})

def order_tracking(request):
    user_orders = Order.objects.filter(user=request.user)
    context = {'orders': user_orders}
    return render(request, 'order_tracking.html', context)

@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.status = status
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'items': items,
        'billing_address': {
            'full_name': order.billing_full_name,
            'email': order.billing_email,
            'address1': order.billing_address1,
            'address2': order.billing_address2,
            'city': order.billing_city,
            'state': order.billing_state,
            'zipcode': order.billing_zipcode,
            'country': order.billing_country,
            'phone': order.billing_phone,
        },
        'shipping_address': {
            'full_name': order.shipping_full_name,
            'email': order.shipping_email,
            'address1': order.shipping_address1,
            'address2': order.shipping_address2,
            'city': order.shipping_city,
            'state': order.shipping_state,
            'zipcode': order.shipping_zipcode,
            'country': order.shipping_country,
            'phone': order.shipping_phone,
        },
        'final_total': order.total,
        'user': request.user
    }
    return render(request, 'order_details.html', context)

def product_services(request):
    return render(request, 'products-services.html')

def hyperdeckcontroller(request):
    return render(request, 'hyperdeckcontroller.html')

def about(request):
    about_content = About.objects.first()
    return render(request, 'about.html', {'about_content': about_content})

def delivery_info(request):
    return render(request, 'information/delivery_info.html')

def privacy_policy(request):
    return render(request, 'information/privacy_policy.html')

def return_refund(request):
    return render(request, 'information/return_refund.html')

def terms_condition(request):
    return render(request, 'information/terms_condition.html')
