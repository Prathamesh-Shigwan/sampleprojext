from .models import CartItem, Cart
from .models import MainCategory


def cart_context(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'total': 0})
        item_count = CartItem.objects.filter(cart=cart).count()
    else:
        item_count = 0

    return {
        'item_count': item_count
    }



def categories_processor(request):
    main_categories = MainCategory.objects.prefetch_related('subcategories').all().order_by('-id')
    return {
        'main_categories': main_categories,
    }
