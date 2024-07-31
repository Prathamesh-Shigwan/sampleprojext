from django.urls import path, include
from . import views
from django.contrib import admin

app_name = 'products'


urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('tinymce/', include('tinymce.urls')),

    path('about/', views.about, name='about'),
    path('delivery_info/', views.delivery_info, name='delivery_info'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('return_refund/', views.return_refund, name='return_refund'),
    path('terms_condition/', views.terms_condition, name='terms_condition'),

    path('product_grid/', views.product_grid, name='product_grid'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_details/', views.product_grid, name='product_details'),
    path('product_details/<str:pid>/', views.product_details, name='product_details'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove-from-wishlist'),

    path('cart/', views.cart_view, name='cart_view'),
    path('add_to_cart/<str:pid>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
    path('process_order/', views.process_order, name='process_order'),
    path('save_info/', views.save_info, name='save_info'),
    path('product_service/', views.product_services, name='product_services'),
    path('order_details/', views.order_details, name='order_details'),
    path('order_tracking/', views.order_tracking, name='order_tracking'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),

    path('category/<str:cid>/', views.product_grid, name='product_grid_by_main_category'),
    path('subcategory/<str:cid>/', views.product_grid, {'is_subcategory': True}, name='product_grid_by_sub_category'),
    path('category/<str:cid>/', views.product_grid, name='product_grid_by_category'),
    path('subcategory/<str:cid>/', views.product_grid, {'is_subcategory': True}, name='product_grid_by_sub_category'),

    path('hyperdeckcontroller/', views.hyperdeckcontroller, name='hyperdeckcontroller'),
]
