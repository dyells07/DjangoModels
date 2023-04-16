from django.shortcuts import render,redirect
from django import forms
from django.http import HttpResponse
from .models import *
from .forms import *
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthorized_user,allowed_users,admin_only
from django.contrib.auth.models import Group

# Create your views here.
# @unauthorized_user 
# def registerPage(request):
    
#     form = CreateUserForm()
#     if request.method=='POST':
#         form=CreateUserForm(request.POST)
#         if form.is_valid():   
#             user=form.save()
#             username=form.cleaned_data.get('username')
#             group = Group.objects.get(name='customer')
#             user.groups.add(group)
#                 # messages.success(request,'Account was created')
#             messages.success(request,'Account was created for '+username)
#             return redirect('login')
#         context={'form':form}
#         return render(request, 'accounts/register.html',context)
 
 
@unauthorized_user 
def registerPage(request):
    
    form = CreateUserForm()
    if request.method=='POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():   
            user=form.save()
            username=form.cleaned_data.get('username')
            
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=user.username,
            )
            print('Account was created for '+username)
            messages.success(request,'Account was created for '+username)
            return redirect('login')
    else:  # Move these lines outside the if statement
        form = CreateUserForm()
    context={'form':form}
    return render(request, 'accounts/register.html',context)

   
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])   
def userPage(request):
    orders=request.user.customer.order_set.all()
    
    total_orders=orders.count()
    delivered_orders=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context={'ORDERS':orders,'title':'User Page','total_orders':total_orders,'delivered_orders':delivered_orders,'pending':pending}
    return render(request, 'accounts/user.html',context)  
 

@unauthorized_user  
def loginPage(request):
    if request.method =='POST':
      username =  request.POST.get('username')
      password = request.POST.get('password')
      
      user=authenticate(request,username=username,password=password)
      if user is not None:
          login(request,user)
          return redirect('home')
      else :
          messages.info(request,'Username or Password is incorrect')
    context={}
    return render(request, 'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return render(request, 'accounts/login.html')



@login_required(login_url='login')
@admin_only  
def home(request):
    orders=Order.objects.all()
    customers=Customer.objects.all()
    
    total_customers=customers.count()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    
    
    
    context={'orders':orders,'customers':customers,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    
    return render(request, 'accounts/dashboard.html',context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])  
def products(request):
    products=Product.objects.all()
    return render(request, 'accounts/product.html',{'products':products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])  
def customer(request,pk_test):
    customer=Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    orders_count=orders.count()
    # customer(request, pk_test)
    myFilter=OrderFilter(request.GET,queryset=orders)
    orders=myFilter.qs
   # orders=customer.order_set.all()
    
    context={'customer':customer,'orders':orders,'orders_count':orders_count,'myFilter':myFilter}
    
    
    return render(request, 'accounts/customer.html',context)


@login_required(login_url='login')
# def products(request):
#     return HttpResponse('Products Page')

# def products(request):
#     return HttpResponse('Products Page')
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order,fields=('product','status'),extra=10)
    customer=Customer.objects.get(id=pk)
    #formset=OrderFormSet(instance=customer)
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    #form=OrderForm(initial={'customer':customer})
    if request.method=='POST':
        print('printing POST',request.POST)
        #form=OrderForm(request.POST)
        formset=OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    #for inline formset 
    #context={'form':form}
    context={'formset':formset}
    
    
    #for empty form
        # context={}
    return render(request, 'accounts/order_form.html',context)            
def updateOrder(request,pk):
    order=Order.objects.get(id=pk)
    form=OrderForm(instance=order)
    if request.method=='POST':
        form=OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request, 'accounts/order_form.html',context)  

def deleteOrder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method=='POST':
        order.delete()
        return redirect('/')
    context={'item':order}
    return render(request, 'accounts/delete.html',context)  
      
         
        
            
            



@login_required
def profile(request):
    user = request.user
    context = {'user': user}
    return render(request, 'accounts/profile.html', context)

# @login_required
# @allowed_users(allowed_roles=['customer'])
# def accountSettings(request):
#     customer = request.user.customer
#     form = CustomerForm(instance=customer)
#     if request.method == 'POST':
#         form = CustomerForm(request.POST, request.FILES, instance=customer)
#         if form.is_valid():
#             form.save()
#     context = {'form': form}
#     return render(request, 'accounts/userSettings.html', context)


# views.py

@login_required
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    profile_pic_url = customer.profile_pic.url if customer.profile_pic else None
    context = {'form': form, 'profile_pic_url': profile_pic_url}
    return render(request, 'accounts/setting.html', context)

