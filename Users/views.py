from getpass import getuser
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import RegisterUserForm, UpdateProfileForm, UpdateUserForm
from .models import User, Profile
from django.contrib.auth.forms import UserChangeForm
from django.views import generic
from django.templatetags.static import static
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'WalnutMind Account Registration'
    email_body = render_to_string('Users/activation.html', {
        'user': user,
        'domain': current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body = email_body, from_email=settings.EMAIL_FROM_USER, to = [user.email])
    email.send()

def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk = uid)
        profile = Profile.objects.get(user = user)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        profile.is_email_verified = True
        profile.save()

        messages.success(request, ("Registration has been successful. Finish setting up your profile."))
        return redirect('loginn')

    return render(request, 'Users/failedactivation.html', {
        'user':user
    })



        
def registerView(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            login(request, user)
            send_activation_email(user, request)
            profile = Profile(
            user = user,
            avatar = 'Users/profile_covers/def_avatar.png',
            banner = 'Users/profile_banners/def_banner.png',
            location = 'US',
            bio = "Hello, I'm new to Walnut Mind!",
            )
            profile.save()
            messages.success(request, ("Your registration is almost complete. Check your email for a verification link."))
            logout(user)
            return redirect('index')
        else:
            messages.success(request, ("An unexpected error occured on our part. Please try again later."))
            return redirect('index')

    else:
        form = RegisterUserForm()
        return render(request,'Users/register.html', {
            'form': form
        })

def loginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        userprofile = Profile.objects.get(user = user)
        if not userprofile.is_email_verified:
            send_activation_email(user, request)
            messages.success(request, ("Your email has not yet been verified. Check your inbox."))
            return redirect('index')

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.success(request, ("There was an error logging in, please try again."))
            return redirect('loginn')
    else:
        return render(request,'Users/login.html')

def logoutView(request):
    logout(request)
    messages.success(request, ("You have successfully signed out."))
    return redirect('index')


# dont know how secure this is- public/private may be able to be changed.
def profileView(request, username):    
    if User.objects.filter(username = username).exists():
        requestedUser = User.objects.get(username = username)

        return render(request, 'Users/profile.html', {
            'user': requestedUser
        })
    else:
        messages.success(request, ("It appears that this user does not exist."))
        return redirect('index')


@login_required(login_url='/users/login')
def editProfileView(request, username):

    if request.method == 'POST':
        if User.objects.filter(username = username).exists():
            requestedUser = User.objects.get(username = username)
            u_form = UpdateUserForm(request.POST, instance = request.user)
            p_form = UpdateProfileForm(request.POST, request.FILES, instance = request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, ("Your account has been successfully updated."))
            return redirect('profile', username = request.user.username)
        else:
            messages.success(request, ("Integrity validation failed. You have attempted to manipulate non-editable fields."))

    else:
        if User.objects.filter(username = username).exists():
            requestedUser = User.objects.get(username = username)
            u_form = UpdateUserForm(instance = request.user)
            p_form = UpdateProfileForm(instance = request.user.profile)
    
    return render(request, 'Users/editprofile.html', {
        'user': requestedUser, 'u_form': u_form, 'p_form': p_form
    })

