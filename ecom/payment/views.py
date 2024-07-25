from django.shortcuts import render, redirect
from cart.cart import Cart
from django.contrib import messages
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from store.models import Product,Profile
from django.contrib.auth.models import User
import datetime

# Create your views here.
def paymentSuccess(request):
    return render(request,"payments.html",{})

def checkout(request):
    cart=Cart(request)
    cart_products=cart.get_products
    quantities= cart.get_quants
    total=cart.total()
    return render(request, "checkout.html", {"cart_products": cart_products,"quantities": quantities,"total":total})

def shipping_form(request):
    if request.user.is_authenticated:
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form=ShippingForm(request.POST or None, instance=shipping_user)
        return render(request,'shipping_form.html',{'shipping_form':shipping_form})
        
    else:
        shipping_form=ShippingForm(request.POST or None)
        return render(request,'shipping_form.html',{'shipping_form':shipping_form})
    
def billing_info(request):
    if request.POST:
        cart=Cart(request)
        cart_products=cart.get_products
        quantities= cart.get_quants
        total=cart.total()
        my_shipping=request.POST
        request.session['my_shipping']=my_shipping
        if request.user.is_authenticated:
            billing_form=PaymentForm()
            return render(request,"billing_info.html", {"cart_products": cart_products,"quantities": quantities,"total":total, 'shipping_info':request.POST , 'billing_form':billing_form})
        
        else:
            billing_form=PaymentForm()
            return render(request,"billing_info.html", {"cart_products": cart_products,"quantities": quantities,"total":total, 'shipping_info':request.POST , 'billing_form':billing_form})
   
    else:
        messages.success(request,"Access denied! Please proceed to checkout again...")
        return redirect('cart_summary')
    
def process_order(request):
    if request.POST:
        cart=Cart(request)
        cart_products=cart.get_products
        quantities= cart.get_quants
        total=cart.total()

        payment_form=PaymentForm(request.POST or None)
        my_shipping=request.session.get('my_shipping')

        shipping_address=f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        full_name=my_shipping['shipping_full_name']
        email=my_shipping['shipping_email']
        amount_paid=total

        if request.user.is_authenticated:
            user=request.user
            create_order=Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id=create_order.pk
            for product in cart_products():
                product_id=product.id
                if product.is_sale:
                    price=product.sale_price
                else:
                    price=product.price
                for key, value in quantities().items():
                    if int(key)==product.id:
                        create_order_item=OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            
            if 'session_key' in request.session:
                del request.session['session_key']

            current_user=Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")
            messages.success(request,"Order Placed!")
            return redirect('index')

        else:
            create_order=Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id=create_order.pk
            for product in cart_products():
                product_id=product.id
                if product.is_sale:
                    price=product.sale_price
                else:
                    price=product.price
                for key, value in quantities().items():
                    if int(key)==product.id:
                        create_order_item=OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            
            
            if 'session_key' in request.session:
                del request.session['session_key']


            messages.success(request,"Order Placed!")
            return redirect('index')
    else:
        messages.success(request,"Access denied! Please proceed to checkout again...")
        return redirect('cart_summary')

def not_shipped_dash(request):  
    if request.user.is_authenticated and request.user.is_superuser:       
        orders=Order.objects.filter(shipped=False)
        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']
            order=Order.objects.filter(id=num)
            now=datetime.datetime.now()
            order.update(shipped=True,date_shipped=now)
            messages.success(request,"Shipping Status Updated.")
            return redirect('index')
        
        return render(request,"not_shipped_dash.html", {"orders":orders})
    else: 
        messages.success(request,"Access Denied!")
        return redirect('index')


def shipped_dash(request):         
    if request.user.is_authenticated and request.user.is_superuser:
        orders=Order.objects.filter(shipped=True)
        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']
            order=Order.objects.filter(id=num)
            now=datetime.datetime.now()
            order.update(shipped=False)           
            messages.success(request,"Shipping Status Updated.")
            return redirect('index')
        
        return render(request,"shipped_dash.html", {"orders":orders})
    else:
        messages.success(request,"Access Denied!")
        return redirect('index')

def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order=Order.objects.get(id=pk)
        items=OrderItem.objects.filter(order=pk)
        if request.POST:
            status=request.POST['shipping_status']
            if status=="true":
                order=Order.objects.filter(id=pk)
                now=datetime.datetime.now()
                order.update(shipped=True,date_shipped=now)

            else:
                order=Order.objects.filter(id=pk)
                order.update(shipped=False)
            messages.success(request,"Shipping Status Updated.")
            return redirect('index')
        return render(request,"orders.html", {"order":order,"items":items})
    else:
        messages.success(request,"Access Denied!")
        return redirect('index')

    