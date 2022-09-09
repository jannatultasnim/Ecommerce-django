from email.message import EmailMessage
from posixpath import split
from django.contrib import messages,auth
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from cart.models import Cart
from cart.views import _cart_id
from cart.models import CartItem
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#user verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

# Create your views here.
def Register(request): #USER REGISTRATION / SIGN UP
    

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            username = email.split('@')[0]
            user = Account.objects.create(first_name=first_name,last_name=last_name,email=email,username=username,password=password) # create user
            user.phone_number =phone_number
            user.save() #save the user info in db 


            #USER ACCOUNT ACTIVATION & sending email via SMTP
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account/user_verification_email.html',
            {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            
            )

            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request, 'Thank You for Registration! We have sent an account activation link to your email!')
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }

    return render (request,'account/register.html', context)


def Login(request):
    if request.method == "POST":
        email = request.POST['email']  #get the email
        password = request.POST.get('password')
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter( cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    #getting product variation by cart id
                    variation_product = []
                    for item in cart_item:
                        ex_variation = item.variation.all()
                        variation_product.append(list(ex_variation))
                    #get cart items from user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    # checking common variations of products by comparing cart variation and user variation list
                    for product in variation_product:
                        if product in ex_var_list:
                            index = ex_var_list.index(product)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user = user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user #assigning the user for a cart
                                item.save()

            except:
                pass
            auth.login(request,user)
            
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print("query--->>",query)
                #next=/cart/checkout/
                params =dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
              
            except:
                return redirect('dashboard')
                
        else:
            messages.error(request,'Incorrect email or password')
            return redirect('login')
    
    
    return render (request,'account/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')

#account activation
def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulation ! you account has been activated!')
        return redirect('login')

    else:
        messages.error(request,'invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def Dashboard(request):

    return render (request,'account/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            message = render_to_string('account/rest_password_email.html',
            {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            )
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')

        else:
            messages.error(request,'Account Does not Exists!')
            return redirect('forgot_password')
    return render(request,'account/forgot_password.html')

def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'please reset your password!')
        return redirect('reset_password')
    else:
        messages.error(request,'this link has been expired')
        return redirect('login')


def reset_password(request):

    if request.method == 'POST':

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:

            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password (password)
            user.save()
            messages.success(request,'your password has been reset!')
            return redirect('login')
        else:
            messages.error(request,'password did not match')

            return redirect('rest_password')

    return render(request,'account/reset_password.html')
    