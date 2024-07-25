# #from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from store.models import Product, Category, Profile
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

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

            current_user=Profile.objects.get(user__id=request.user.id)
            saved_cart=current_user.old_cart
            if saved_cart:
                converted_cart=json.loads(saved_cart)
                cart=Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

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
            messages.success(request, ("You have been registered successfully! Kindly fill out your user info."))
            return redirect('update_info')
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
    
def category_summary(request):
        categories=Category.objects.all()
        return render(request, 'category_summary.html', {"categories":categories})

def update_user(request):
    if request.user.is_authenticated:
        current_user=User.objects.get(id=request.user.id)
        user_form=UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request,"User Profile has been updated successfully.")
            return redirect('index')
        return render(request,'update_user.html',{'user_form':user_form})
    else:
        messages.success(request, ("You must be logged in to update your profile successfully."))
        return redirect('index')

    return render(request, 'update_user.html', {})

def update_password(request):
    if request.user.is_authenticated:
        current_user=request.user
        if request.method =='POST':
            form=ChangePasswordForm(current_user,request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,"User Password has been updated successfully.")
                login(request, current_user)
                return redirect('index')
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error)
                    return redirect('update_password')

            
        else:
            form=ChangePasswordForm(current_user)
            return render(request, "update_password.html",{'form':form})
    else:
        messages.success(request, ("You must be logged in to update your profile successfully."))
        return redirect('index')
        
def update_info(request):
    if request.user.is_authenticated:
        current_user=Profile.objects.get(user__id=request.user.id)
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        form=UserInfoForm(request.POST or None, instance=current_user)
        shipping_form=ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request,"Your User Info has been updated successfully.")
            return redirect('index')
        return render(request,'update_info.html',{'form':form,'shipping_form':shipping_form})
    else:
        messages.success(request, ("You must be logged in to update your profile successfully."))
        return redirect('index')

    return render(request, 'update_info.html', {})

def search(request):
    if request.method=="POST":
        searched=request.POST.get('searched','')
        searched=Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched: 
            messages.success(request,"That product does not exist... Please search for something else instead.")
            return render(request,"search.html",{})
        else:
            return render(request,"search.html",{'searched':searched})
    else:
        return render(request,"search.html",{})
    
