from django.contrib import admin
from django.utils.html import mark_safe
from .models import *

class ProductImagesAdmin(admin.TabularInline):
    model = ExtraImages
    extra = 1
    can_delete = True  # Allow deletion of extra images

    def has_delete_permission(self, request, obj=None):
        return True  # Enable delete permission for the inlines

    def has_add_permission(self, request, obj=None):
        return True  # Enable add permission for the inlines


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'main_category_display', 'sub_category_display', 'price', 'product_status', 'product_image_display')
    search_fields = ('name', 'title', 'description')
    list_filter = ('main_category', 'sub_category', 'product_status')
    inlines = [ProductImagesAdmin]

    def main_category_display(self, obj):
        return obj.main_category.title if obj.main_category else 'No Main Category'
    main_category_display.short_description = 'Main Category'

    def sub_category_display(self, obj):
        return obj.sub_category.title if obj.sub_category else 'No Sub Category'
    sub_category_display.short_description = 'Sub Category'

    def product_image_display(self, obj):
        if obj.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
        return "No Image"
    product_image_display.short_description = 'Image Preview'

class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_image_display')
    search_fields = ('title',)

    def category_image_display(self, obj):
        return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
    category_image_display.short_description = 'Image Preview'

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_category', 'subcategory_image_display')
    search_fields = ('title',)
    list_filter = ('parent_category',)

    def subcategory_image_display(self, obj):
        return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
    subcategory_image_display.short_description = 'Image Preview'

class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ('product', 'quantity', 'line_total', 'product_image')
    extra = 0
    can_delete = True  # Allow deletion of cart items

    def has_add_permission(self, request, obj=None):
        return True  # Allow adding cart items

    def has_delete_permission(self, request, obj=None):
        return True  # Enable delete permission for cart items


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'updated', 'timestamp')
    search_fields = ('user__username', 'id')
    inlines = [CartItemInline]

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'line_total', 'product_image')
    search_fields = ('cart__id', 'product__name', 'product__sku')

    def has_add_permission(self, request):
        return True  # Allow adding cart items

    def has_change_permission(self, request, obj=None):
        return True  # Allow changing cart items

    def has_delete_permission(self, request, obj=None):
        return True  # Enable delete permission for cart items

class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendors_image']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price', 'product_image')
    can_delete = True  # Allow deletion of order items
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False  # Disallow adding order items inline

    def has_delete_permission(self, request, obj=None):
        return True  # Enable delete permission for order items


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'payment_method', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'status')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'product_image')
    list_filter = ('order__status', 'product')
    search_fields = ('order__id', 'product__name', 'user__username')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'get_ratings']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'date', 'display_name')

    def display_name(self, obj):
        return str(obj)

    display_name.short_description = "Wishlist Entry"

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'status']

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user']

class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user']

class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'discount_amount', 'discount_percentage', 'valid_from', 'valid_to', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    list_editable = ['discount_amount', 'discount_percentage', 'valid_from', 'valid_to', 'active']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['shipping_charge']

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product_sku', 'product', 'stock_quantity', 'last_updated', 'product_image')
    list_filter = ('last_updated',)
    search_fields = ('product__name', 'product__sku')

    def product_sku(self, obj):
        return obj.product.sku

    product_sku.short_description = "SKU"

    def product_image(self, obj):
        return obj.product_image()

    product_image.short_description = "Image"
    product_image.allow_tags = True

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)
admin.site.register(ProductsReviews, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(DiscountCode, DiscountCodeAdmin)
admin.site.register(MainCategory, MainCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
