from django.shortcuts import render
from store.models import *


def home(request):
    products = Product.objects.all().filter(is_availble = True)
    context = {
        'products' : products ,
    }
    return render(request , "home.html" , context)