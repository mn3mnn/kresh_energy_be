from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.utils import translation

if typing.TYPE_CHECKING:
    from allauth.account.models import EmailConfirmation
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from kresh_energy_be.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_email_confirmation_url(
        self,
        request: HttpRequest,
        emailconfirmation: EmailConfirmation,
    ) -> str:
        """Points the confirmation link at the frontend instead of the
        backend's own placeholder route.

        dj-rest-auth's `account_confirm_email` URL is a bare TemplateView
        with no template — it exists only so reverse() resolves when
        building this link, and 500s if a browser visits it directly. The
        frontend has its own `/verify-email` page that reads `key` from the
        query string and POSTs it to the real
        `/api/auth/registration/verify-email/` endpoint.

        Locale is baked into the URL (not left to the frontend's
        `localeDetection: false` default-locale redirect) since we already
        know the visitor's active locale from this same request.
        """
        locale = translation.get_language()
        locale = locale if locale == "en" else "de"
        return f"{settings.FRONTEND_URL}/{locale}/verify-email?key={emailconfirmation.key}"


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
