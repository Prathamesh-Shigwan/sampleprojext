# accounts/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, UserInfoForm, OTPVerificationForm
from django.conf import settings
from .models import User, Profile
from products.forms import ShippingForm, BillingForm
from products.models import ShippingAddress, BillingAddress
from django_otp.plugins.otp_email.models import EmailDevice

def sign_up(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)  # Do not save the user yet
            new_user.is_active = False  # Deactivate account till it is verified
            new_user.save()
            device, created = EmailDevice.objects.get_or_create(user=new_user, name='default')
            device.generate_challenge()  # Generate and send OTP
            request.session['user_id'] = new_user.id  # Store user ID in session
            messages.success(request, 'An OTP has been sent to your email. Please verify to complete the registration.')
            return redirect('accounts:verify_signup_otp')
    else:
        form = UserRegisterForm()
    context = {'form': form}
    return render(request, 'signup.html', context)

def verify_signup_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired, please sign up again.")
        return redirect('accounts:sign_up')

    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            device = EmailDevice.objects.get(user=user, name='default')
            if device.verify_token(otp):
                user.is_active = True  # Activate the user
                user.save()
                login(request, user)  # Log the user in
                messages.success(request, "Your account has been verified and you are now logged in.")
                return redirect("accounts:user_profile")
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPVerificationForm()

    context = {'form': form}
    return render(request, 'verify_signup_otp.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"You are already logged in as {request.user}.")
        return redirect('products:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(email=email, password=password)

            if user is not None:
                device, created = EmailDevice.objects.get_or_create(user=user, name='default')
                device.generate_challenge()
                request.session['email'] = email
                request.session['password'] = password
                return redirect('accounts:verify_otp')
            else:
                messages.warning(request, f"User Does Not Exist, create an account")

        except:
            messages.warning(request, f"User with {email} does not exist")

    context = {'form': UserRegisterForm()}
    return render(request, 'login.html', context)

def verify_otp(request):
    email = request.session.get('email')
    password = request.session.get('password')
    if not email or not password:
        messages.error(request, "Session expired, please login again.")
        return redirect('accounts:login')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user = authenticate(email=email, password=password)
            device = EmailDevice.objects.get(user=user, name='default')
            if device.verify_token(otp):
                login(request, user)
                messages.success(request, "Logged in successfully")
                return redirect("accounts:user_profile")
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPVerificationForm()

    context = {'form': form}
    return render(request, 'verify_otp.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')

def user_profile(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UserUpdateForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('home')
        return render(request, 'user-profile.html', {'user_form': user_form})
    else:
        messages.success(request, "You need to be logged in to update your profile.")
        return redirect('home')

def update_info(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect('accounts:login')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    shipping_address, _ = ShippingAddress.objects.get_or_create(user=request.user)

    billing_address, shipping_address = None, None
    try:
        billing_address = BillingAddress.objects.get(user=request.user)
    except BillingAddress.DoesNotExist:
        pass
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        pass

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

            messages.success(request, "Your billing and shipping information has been updated.")
            return redirect('products:checkout')
    else:
        billing_form = BillingForm(instance=billing_address)
        shipping_form = ShippingForm(instance=shipping_address)

    context = {
        'billing_form': billing_form,
        'shipping_form': shipping_form
    }
    return render(request, 'update_info.html', context)
