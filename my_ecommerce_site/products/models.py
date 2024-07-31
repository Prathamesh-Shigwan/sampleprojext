from datetime import timezone
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from accounts.models import User
from decimal import Decimal
from tinymce.models import HTMLField


STATUS_CHOICES = {
    ('process', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered')
}

STATUS = {
    ('draft', 'Draft'),
    ('disabled', 'Disabled'),
    ('rejected', 'Rejected'),
    ('in_review', 'IN Review'),
    ('published', 'Published'),
}

RATING = {
    (1, "★✩✩✩✩"),
    (2, "★★✩✩✩"),
    (3, "★★★✩✩"),
    (4, "★★★★✩"),
    (5, "★★★★★")
}

def user_directory_path(instance, filename):
    # Check if the instance has a direct user attribute
    if hasattr(instance, 'user'):
        return 'user_{0}/{1}'.format(instance.user.id, filename)
    # Check if the instance has a product attribute with a related user
    elif hasattr(instance, 'product') and hasattr(instance.product, 'user'):
        return 'user_{0}/{1}'.format(instance.product.user.id, filename)
    # Default to a generic path if no user can be found
    return 'unknown_user/{0}'.format(filename)

def category_directory_path(instance, filename):
    if hasattr(instance, 'cid'):
        return 'category_{0}/{1}'.format(instance.cid, filename)
    return 'category_{0}/{1}'.format(instance.id, filename)

def supplier_directory_path(instance, filename):
    return 'supplier_{0}/{1}'.format(instance.Vid, filename)

class MainCategory(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefghijklmnop1234567890")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=category_directory_path)
    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2, null=True)

    class Meta:
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    sid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="subcat", alphabet="abcdefghijklmnop1234567890")
    parent_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=category_directory_path)
    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2, null=True)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def subcategory_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Tags(models.Model):
    tname = models.CharField(max_length=100)


class Supplier(models.Model):
    Vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven", alphabet="abcdefghijklmnop1234567890")
    item = models.CharField(max_length=50)
    image = models.ImageField(upload_to=supplier_directory_path)
    name = models.CharField(max_length=50)
    mail = models.EmailField()
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Suppliers"

    def vendors_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.name


class Product(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    pid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven", alphabet="abcdefghijklmnop1234567890")
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)  # Add this line

    image = models.ImageField(upload_to=user_directory_path)
    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)
    old_price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)
    specification = models.TextField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    main_category = models.ForeignKey(MainCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review") # 4 CHAR ONLY IN idS

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    featured = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length=10, max_length=15, prefix="sku", alphabet="1234567890abcdefghijklmnop")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.name

    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price


class ProductVariant(models.Model):
    COLOR_CHOICES = [
        ('grey', 'Grey'),
        ('lemon', 'Lemon'),
        ('white', 'White'),
        ('red', 'Red'),
        ('black', 'Black'),
        ('pink', 'Pink'),
    ]

    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    stock_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'color', 'size', 'gender')

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size} - {self.gender}"

    def product_image(self):
        if self.product.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.product.image.url))
        return "(No Image)"


class ExtraImages(models.Model):
    image = models.ImageField(upload_to=user_directory_path)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images')  # Update related_name
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ExtraImages"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return f"Image for {self.product.name}"




################################ cart Order ####################

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, help_text="Fixed discount amount")
    discount_percentage = models.IntegerField(blank=True, null=True, help_text="Percentage discount, if applicable")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text="Minimum spending amount required to apply this code")

    def is_valid(self):
        current_time = timezone.now()
        return self.active and self.valid_from <= current_time <= self.valid_to
    def __str__(self):
        return self.code


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')

    def update_total(self):
        self.total = sum(item.line_total for item in self.cartitem_set.all())
        self.save()

    def apply_discount(self):
        print(f"Applying discount: Current total before discount: {self.total}")
        if self.discount_code and self.discount_code.is_valid():
            current_time = timezone.now()
            if self.discount_code.active and self.discount_code.valid_from <= current_time <= self.discount_code.valid_to:
                discount_value = Decimal('0.00')
                if self.discount_code.discount_amount:
                    discount_value = self.discount_code.discount_amount
                    self.total -= discount_value
                elif self.discount_code.discount_percentage:
                    discount_value = (self.discount_code.discount_percentage / 100.0) * self.total
                    self.total -= discount_value
                self.total = max(Decimal('0.00'), self.total)  # Prevent negative totals
                print(f"Discount applied: {discount_value}")
                return discount_value
        print("No valid discount found or applied.")
        return Decimal('0.00')

    def __str__(self):
        return f"Cart id: {self.id}"

    def save(self, *args, **kwargs):
        if self.discount_code and self.discount_code.is_valid():
            self.apply_discount()
        super().save(*args, **kwargs)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def product_image(self):
        if self.product.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.product.image.url))
        return "(No Image)"
    product_image.short_description = 'Product Image'

    def __str__(self):
        return self.product.name


    def __str__(self):
        return self.product.name


############################# Product Review ########################


class ProductsReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.ImageField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Products Reviews"

    def __str__(self):
        return self.product.name

    def get_ratings(self):
        return self.rating


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        user_name = self.user.username if self.user else "No User"
        product_name = self.product.name if self.product else "No Product"
        return f"{user_name} - {product_name}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    shipping_full_name = models.CharField(max_length=300)
    shipping_email = models.EmailField(max_length=300)
    shipping_address1 = models.CharField(max_length=300)
    shipping_address2 = models.CharField(max_length=300)
    shipping_city = models.CharField(max_length=300)
    shipping_state = models.CharField(max_length=300)
    shipping_zipcode = models.CharField(max_length=300)
    shipping_country = models.CharField(max_length=300)
    shipping_phone = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    billing_full_name = models.CharField(max_length=300)
    billing_email = models.EmailField(max_length=300)
    billing_address1 = models.CharField(max_length=300)
    billing_address2 = models.CharField(max_length=300)
    billing_city = models.CharField(max_length=300)
    billing_state = models.CharField(max_length=300)
    billing_zipcode = models.CharField(max_length=300)
    billing_country = models.CharField(max_length=300)
    billing_phone = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "Billing Address"

    def __str__(self):
        return f'Billing Address - {str(self.id)}'


class SiteSettings(models.Model):
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'), help_text="Default shipping charge")

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


############################# Order  ########################

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Billing address fields
    billing_full_name = models.CharField(max_length=300)
    billing_email = models.EmailField(max_length=300)
    billing_address1 = models.CharField(max_length=300)
    billing_address2 = models.CharField(max_length=300, blank=True, null=True)
    billing_city = models.CharField(max_length=300)
    billing_state = models.CharField(max_length=300)
    billing_zipcode = models.CharField(max_length=300)
    billing_country = models.CharField(max_length=300)
    billing_phone = models.CharField(max_length=300)

    # Shipping address fields
    shipping_full_name = models.CharField(max_length=300)
    shipping_email = models.EmailField(max_length=300)
    shipping_address1 = models.CharField(max_length=300)
    shipping_address2 = models.CharField(max_length=300, blank=True, null=True)
    shipping_city = models.CharField(max_length=300)
    shipping_state = models.CharField(max_length=300)
    shipping_zipcode = models.CharField(max_length=300)
    shipping_country = models.CharField(max_length=300)
    shipping_phone = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'Order {self.id} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

    def product_image(self):
        if self.product.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.product.image.url))
        return "(No Image)"

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_quantity = models.IntegerField(default=0, verbose_name="Stock Quantity")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def product_image(self):
        if (self.product.image):
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.product.image.url))
        return "(No Image)"

    def __str__(self):
        return f"{self.product.name} - SKU {self.product.sku} - Stock: {self.stock_quantity}"


class About(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()
    image = models.ImageField(upload_to='about_images/', blank=True, null=True)

    def __str__(self):
        return self.title
