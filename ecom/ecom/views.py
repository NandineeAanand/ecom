# #from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django import forms
from .forms import SignUpForm
from store.models import Product
from store.models import Category

def index(request):
#     #return HttpResponse("Hello Universe! I am home.")
    return render(request, 'index.html')

def about(request):
#        # return HttpResponse("My About page.")
    return render(request, 'about.html')

def login_user(request):
    if request.method=='POST':
        username= request.POST['username']
        email= request.POST['email']
        password= request.POST['password']
        user=authenticate(request,username=username,email=email,password=password)
        if user is not None:
            login(request,user)
            messages.success(request, ("You have been Logged in successfully."))
            return redirect('index')
        else:
            messages.success(request, ("There was an error, Log in again."))
            return redirect('login')   
    else: 
        return render(request,  'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been sucessfully logged out.."))
    return redirect('index')

def contact(request):
    return render(request, 'contact.html')

def register(request):
    form=SignUpForm()
    if request.method =="POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user= authenticate(request,username=username, password=password)
            login(request,user)
            messages.success(request, ("You have been registered!"))
            return redirect('index')
        else:
            messages.success(request, ("There was a problem!Please register again."))
            return redirect('index')
    else:
        return render(request, 'register.html',{'form':form})
    
def category_view(request, xyz):
    xyz=xyz.replace('-',' ')


    try:
        category = Category.objects.get(name=xyz.replace('-', ' '))
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.error(request, "This category doesn't exist! Please try something different.")
        return redirect('index')
    # try:
    #     category=Category.objects.get(name='xyz')
    #     products=Product.objects.filter(category=category)
    #     return render(request, 'category.html',{'products':products,'category':category})

    # except:
    #     messages.success(request, ("This category doesn't exists!Please try something different."))
    #     return redirect('index')