from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation

from kresh_energy_be.users.models import User

_REWARD_EARNED_SUBJECTS = {
    "de": "Du hast eine Empfehlungsprämie verdient!",
    "en": "You earned a referral reward!",
}
_REFERRAL_SIGNUP_SUBJECTS = {
    "de": "Jemand hat sich mit deinem Empfehlungscode registriert",
    "en": "Someone signed up with your referral code",
}
_DISCOUNT_APPLIED_SUBJECTS = {
    "de": "Dein Empfehlungsrabatt wurde angewendet",
    "en": "Your referral discount was applied",
}


def _normalize_locale(locale: str | None) -> str:
    return locale if locale == "en" else "de"


def _send(subjects: dict, template_prefix: str, locale: str, to: str, context: dict) -> None:
    """Best-effort send: never raises, so a broken mailbox never breaks the
    caller's transaction."""
    if not to:
        return
    locale = _normalize_locale(locale)
    context = {**context, "locale": locale}
    with translation.override(locale):
        text_body = render_to_string(f"{template_prefix}.txt", context)
        html_body = render_to_string(f"{template_prefix}.html", context)

    message = EmailMultiAlternatives(
        subject=subjects[locale],
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=True)


def send_referral_reward_email(referrer: User, amount: Decimal, locale: str = "de") -> None:
    """Notify a referrer they earned a reward."""
    _send(
        _REWARD_EARNED_SUBJECTS,
        "referrals/email/reward_earned",
        locale,
        referrer.email,
        {"referrer": referrer, "amount": amount},
    )


def send_referral_signup_email(referrer: User) -> None:
    """Notify a referrer that someone just signed up with their code.

    Fires before any reward is earned (that's `send_referral_reward_email`,
    triggered later by the referred person's first qualifying submission).
    Language is best-effort from the current request's active language,
    since signup happens before we have any stored locale for this referral.
    """
    _send(
        _REFERRAL_SIGNUP_SUBJECTS,
        "referrals/email/referral_signup",
        translation.get_language(),
        referrer.email,
        {"referrer": referrer},
    )


def send_referred_discount_applied_email(user: User, amount: Decimal, locale: str = "de") -> None:
    """Confirm to the referred person that their signup discount was
    auto-applied to the quote/booking they just submitted."""
    _send(
        _DISCOUNT_APPLIED_SUBJECTS,
        "referrals/email/discount_applied",
        locale,
        user.email,
        {"user": user, "amount": amount},
    )
