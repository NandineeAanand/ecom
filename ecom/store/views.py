from django.shortcuts import render,redirect
from .models import Product
from .models import Category
from django.contrib import messages

# Create your views here.
def store(request):
    products =Product.objects.all()
    return render(request, 'store.html',{'products':products})

def product(request,pk):
    products =Product.objects.get(id=pk)
    return render(request, 'product.html',{'product':products})


