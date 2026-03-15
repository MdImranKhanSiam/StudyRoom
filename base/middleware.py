from django.shortcuts import redirect

class BlockDirectGoogleCallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        callback_path = '/accounts/google/login/callback/'

        # If user is already logged in, skip callback URL entirely
        if request.user.is_authenticated and request.path == callback_path:
            return redirect('/')  # send them home

        # Otherwise, block if 'code' param is missing
        if request.path == callback_path and 'code' not in request.GET:
            return redirect('/')  # redirect to homepage

        return self.get_response(request)