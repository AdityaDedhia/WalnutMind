from Users.models import Blacklist
from django.contrib.auth import logout
from django.shortcuts import render
from Users.utils import get_ip

def BlacklistBlockMiddleware(get_response):
    def middleware(request):
        response = get_response(request)
        #GET USER LOCATION and RUN through Blacklisted IPs.
        ip = get_ip(request)
        if Blacklist.objects.filter(ip = ip) and ip != '127.0.0.1': #Permit localhost
            logout(request)
            return render(request, "blacklist.html")
        return response
    return middleware