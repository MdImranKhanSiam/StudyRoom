from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from . models import UserProfile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Called when a social authentication attempt fails.
        We'll redirect the user to the homepage.
        """
        return redirect('/')

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data

        name = data.get('name')
        avatar = data.get('picture')

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'display_name': name,
                'avatar': avatar,
            }
        )

        return user
