from django.shortcuts import render
from Store.models import Product
def Home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'product': products
    }
    return render(request,'home.html',context)