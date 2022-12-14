from django.shortcuts import render,get_object_or_404
from . models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
#FOR PAGINATION
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator # 


# Create your views here.

def store(request,category_slug=None):
    categories = None
    products = None
    if category_slug is not None: #DISPLAY THE PRODUCTS IN EACH CATEGORY
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        paginator= Paginator(products,1)
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
        product_count = products.count()
    else:                        #DISPLAY PRODUCTS OF ALL CATEGORY
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator= Paginator(products,3) #LIMIT THE NUMBER OF ITEM DISPLAY ON STORE
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'product':page_products,
        'product_count': product_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug): #TO SHOW ITEMS DETAIL
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
   
    context = {
        'single_products': single_product, 
        'in_cart': in_cart,}
    
    return render(request,'store/product_detail.html',context)

def Search(request): # search functionality/SEARCHING ITEMS
    if 'keyword' in request.GET:
        value= request.GET['keyword']
        if value:
            products = Product.objects.order_by('-created_date').filter(description__icontains=value)
    context={
        'product': products,
        }
    return render(request,'store/store.html',context)
