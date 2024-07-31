# forms.py

from django import forms
from django.contrib import admin
from .models import *


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name*', 'class': 'your-css-class'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Mail*', 'class': 'your-css-class'}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Subject*', 'class': 'your-css-class'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'class': 'your-css-class'}))


class DiscountCodeAdminForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        fields = '__all__'

class DiscountCodeAdmin(admin.ModelAdmin):
    form = DiscountCodeAdminForm
    # Other properties remain the same

class DiscountForm(forms.Form):
    code = forms.CharField(label='Discount Code', max_length=50)


class ShippingForm(forms.ModelForm):
    shipping_full_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Full name'}), max_length=50)
    shipping_email = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), max_length=50)
    shipping_address1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Addresss line 1'}), max_length=50)
    shipping_address2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address line 2'}), max_length=50)
    shipping_city = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}), max_length=50)
    shipping_state = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}), max_length=50)
    shipping_zipcode = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zipcode'}), max_length=50)
    shipping_country = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Country'}), max_length=50)
    shipping_phone = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}), max_length=50)

    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_email', 'shipping_address1','shipping_address2','shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country', 'shipping_phone']
        exclude = ['user']


class BillingForm(forms.ModelForm):
    billing_full_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Full name'}), max_length=50)
    billing_email = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), max_length=50)
    billing_address1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Addresss line 1'}), max_length=50)
    billing_address2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address line 2'}), max_length=50)
    billing_city = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}), max_length=50)
    billing_state = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}), max_length=50)
    billing_zipcode = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zipcode'}), max_length=50)
    billing_country = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Country'}), max_length=50)
    billing_phone = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}), max_length=50)

    class Meta:
        model = BillingAddress
        fields = ['billing_full_name', 'billing_email', 'billing_address1','billing_address2','billing_city', 'billing_state', 'billing_zipcode', 'billing_country', 'billing_phone']
        exclude = ['user']



class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']