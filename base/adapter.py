from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from . models import UserProfile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.socialaccount_set.exists() and request.user.last_login is None:
            return resolve_url("/")
        return resolve_url("/")

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
