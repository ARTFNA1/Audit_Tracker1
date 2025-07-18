from django.shortcuts import redirect
from django.urls import reverse

class EnsureUserHasRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return self.get_response(request)
            if not request.path.startswith('/admin/profile/') and request.path.startswith('/admin'):
                if hasattr(request.user, 'profile') and not request.user.profile.role:
                    return redirect(reverse('admin:select_role'))
        return self.get_response(request)