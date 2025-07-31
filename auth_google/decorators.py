from django.shortcuts import redirect

def google_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'credentials' not in request.session:
            return redirect('google_login')  # or hardcode: /google/login/
        return view_func(request, *args, **kwargs)
    return wrapper
