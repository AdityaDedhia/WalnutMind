from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterUserForm, UpdateProfileForm, UpdateUserForm
from .models import User, Profile, Highlight
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
import threading

class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


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
    EmailThread(email).start()

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

        messages.success(request, ("Registration has been successful. You may now login."))
        return redirect('loginn')

    return render(request, 'Users/failedactivation.html', {
        'user':user
    })
        
def registerView(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            form.save()
            user = authenticate(request=request, username = username, password = password)
            send_activation_email(user, request)
            #GET USER LOCATION
            x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forw_for is not None:
                ip = x_forw_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            location = GeoIP2().country(ip)
            #INSTANTIATE USER PROFILE
            profile = Profile(
            user = user,
            avatar = 'Users/profile_covers/def_avatar.png',
            banner = 'Users/profile_banners/def_banner.png',
            location = location,
            interests = 'None',
            bio = "Hello, I'm new to Walnut Mind!",
            )
            profile.save()
            messages.success(request, ("Your registration is almost complete. Check your email for a verification link."))
            return redirect('index')
        else:
            messages.success(request, ("The form details you entered were invalid. Please verify them again."))
            return redirect('registerr')

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
        if user is not None:
            userprofile = Profile.objects.get(user = user)
            #GET USER LOCATION
            x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forw_for is not None:
                ip = x_forw_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            location = GeoIP2().country(ip)
            #BLOCK INTERNATIONAL LOGIN ATTEMPTS
            if not userprofile.location == location:
                messages.success(request, ("Unauthorized login attempt blocked. You are now being monitored for suspicious activity."))
                return redirect('index')
            #FORCE PROFILE VERIFICATION
            if not userprofile.is_email_verified:
                send_activation_email(user, request)
                messages.success(request, ("Your email has not yet been verified. Check your inbox."))
                return redirect('index')
            login(request, user)
            return redirect('index')
        else:
            messages.success(request, ("The username and/or password you have entered is incorrect, please try again."))
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
        articles = requestedUser.articlepublisher.all()
        commentaries = requestedUser.commentarypublisher.all()
        diaries = requestedUser.diarypublisher.all()
        highlights = Highlight.objects.filter(author = requestedUser)

        return render(request, 'Users/profile.html', {
            'user': requestedUser, 'articles':articles, 'commentaries': commentaries, 'diaries': diaries, 'highlights': highlights
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