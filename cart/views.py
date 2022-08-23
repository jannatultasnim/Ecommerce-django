from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from Store.models import Product,Variation
from . models import Cart, CartItem

# Create your views here.
def _cart_id(request): # get cart id from the session id
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def add_cart (request,product_id):
    product = Product.objects.get(id = product_id) #get the product
    variation_product = [] #getting product variation
    if request.method == 'POST':
        for i in request.POST:
            key = i
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact = key, variation_value__iexact = value)
                variation_product.append(variation)
            except Variation.DoesNotExist:
                pass
        
    

    try:    #getting the cart
        cart = Cart.objects.get(cart_id =_cart_id(request)) #get the cart by id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product,cart=cart)
        #existing variation --> coming from database
        #current variation ---> product variation
        #item_id ---> coming from database
        ex_var_list=[]
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        print(ex_var_list)

        if variation_product in ex_var_list:
           #INCREASE THE ITEM QUANTITY
           index = ex_var_list.index(variation_product)
           item_id = id[index]
           item = CartItem.objects.get(product=product, id=item_id)
           item.quantity+=1
           item.save()
        else:
            # ADD NEW ITEM
            item = CartItem.objects.create(product=product,quantity=1,cart=cart)

            if len(variation_product) > 0:
                item.variation.clear()
                item.variation.add(*variation_product)
        #cart_item.quantity+=1
            item.save()
    else:
        cart_item = CartItem.objects.create(product=product,quantity=1, cart=cart)
        if len(variation_product) > 0:
            cart_item.variation.clear()
            
            cart_item.variation.add(*variation_product)
        cart_item.save()
    
    return redirect('cart')

def remove_cart(request,product_id,cart_item_id): # remove the quantity of items in the cart
    cart = Cart.objects.get(cart_id = _cart_id(request)) #get the id of cart from the session
    product = get_object_or_404(Product,id=product_id) #get the product id from the product model
    try:

        cart_items = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_items.quantity > 1:
            cart_items.quantity -= 1
            cart_items.save()
        else:
            cart_items.delete()
    except:
        pass
    return redirect ('cart')
def remove_cart_item(request,product_id,cart_item_id): # remove cart items
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_items = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_items.delete()
    return redirect('cart')


def cart(request, total = 0, quantity=0, cart_items=None): #creates cart
    try:
        cart = Cart.objects.get(cart_id =_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for i in cart_items:
            total += (i.product.price * i.quantity)
            quantity += i.quantity
        tax_amount  = (2*total/100)
        grand_total = total+tax_amount
    except CartItem.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_item': cart_items,
        'tax': tax_amount,
        'Grand_total': grand_total,

    }

    return render (request,'store/cart.html',context)