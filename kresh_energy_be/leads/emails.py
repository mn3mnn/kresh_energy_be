from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation

from .models import InspectionBooking
from .models import QuoteRequest

_QUOTE_SUBJECTS = {
    "de": "Deine Angebotsanfrage bei Kresh EcoSolaris ist eingegangen",
    "en": "We've received your Kresh EcoSolaris quote request",
}
_BOOKING_SUBJECTS = {
    "de": "Deine Terminanfrage bei Kresh EcoSolaris ist eingegangen",
    "en": "We've received your Kresh EcoSolaris inspection booking",
}
_QUOTE_PRICE_SUBJECTS = {
    "de": "Dein persönliches Angebot von Kresh EcoSolaris",
    "en": "Your personal quote from Kresh EcoSolaris",
}


def _send(subjects: dict, template_prefix: str, locale: str, to: str, context: dict) -> None:
    """Best-effort confirmation send: never raises, so a broken mailbox
    never breaks the public lead-submission endpoint."""
    if not to:
        return
    locale = locale if locale == "en" else "de"
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


def send_quote_confirmation_email(quote: QuoteRequest) -> None:
    _send(
        _QUOTE_SUBJECTS,
        "leads/email/quote_confirmation",
        quote.locale,
        quote.email,
        {"quote": quote},
    )


def send_booking_confirmation_email(booking: InspectionBooking) -> None:
    _send(
        _BOOKING_SUBJECTS,
        "leads/email/booking_confirmation",
        booking.locale,
        booking.email,
        {"booking": booking},
    )


def send_quote_price_email(quote: QuoteRequest, price: Decimal) -> None:
    """Send the admin-entered price to the customer. Triggered manually from
    the QuoteRequest admin change page (see QuoteRequestAdmin.response_change)
    — this is not sent automatically on submission."""
    _send(
        _QUOTE_PRICE_SUBJECTS,
        "leads/email/quote_price",
        quote.locale,
        quote.email,
        {"quote": quote, "price": price},
    )
