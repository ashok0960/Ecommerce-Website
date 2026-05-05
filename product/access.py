from django.shortcuts import redirect
from django.contrib import messages

def vendor_only(view_function):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_staff and request.user.is_authenticated:
            return view_function(request, *args, **kwargs)
        else:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('/')
    return wrapper_function