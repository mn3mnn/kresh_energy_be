from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from kresh_energy_be.users.models import User


def send_referral_reward_email(referrer: User, amount: Decimal) -> None:
    """Notify a referrer they earned a reward. Best-effort: never raises."""
    if not referrer.email:
        return

    context = {"referrer": referrer, "amount": amount}
    text_body = render_to_string("referrals/email/reward_earned.txt", context)
    html_body = render_to_string("referrals/email/reward_earned.html", context)

    message = EmailMultiAlternatives(
        subject="You earned a referral reward!",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[referrer.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=True)
