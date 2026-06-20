from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class LeadStatus(models.TextChoices):
    NEW = "new", _("New")
    CONTACTED = "contacted", _("Contacted")
    QUOTED = "quoted", _("Quoted")
    WON = "won", _("Won")
    LOST = "lost", _("Lost")


class RoofType(models.TextChoices):
    PITCHED = "pitched", _("Pitched roof")
    FLAT = "flat", _("Flat roof")
    OTHER = "other", _("Other")


class QuoteRequest(TimeStampedModel):
    """A request for a solar quotation submitted from the website."""

    full_name = models.CharField(_("Full name"), max_length=160)
    phone = models.CharField(_("Phone"), max_length=40)
    email = models.EmailField(_("Email"))
    address = models.TextField(_("Address"))
    notes = models.TextField(_("Additional notes"), blank=True)

    electricity_bill = models.FileField(
        _("Electricity bill"),
        upload_to="quotes/bills/",
        blank=True,
    )
    meter_photo = models.ImageField(
        _("Meter photo"),
        upload_to="quotes/meters/",
        blank=True,
    )

    # Optional snapshot of the solar-calculator result that led to the request.
    calc_monthly_bill = models.DecimalField(
        _("Monthly bill (€)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    calc_system_size_kwp = models.DecimalField(
        _("Estimated system size (kWp)"),
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    calc_roof_type = models.CharField(
        _("Roof type"),
        max_length=20,
        choices=RoofType.choices,
        blank=True,
    )
    wants_battery = models.BooleanField(_("Wants battery"), default=False)
    wants_ev_charger = models.BooleanField(_("Wants EV charger"), default=False)

    locale = models.CharField(_("Locale"), max_length=5, default="de")
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
    )

    class Meta:
        verbose_name = _("Quote request")
        verbose_name_plural = _("Quote requests")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.created:%Y-%m-%d})"


class QuoteRoofPhoto(models.Model):
    """A roof photo attached to a quote request (multiple per request)."""

    quote = models.ForeignKey(
        QuoteRequest,
        related_name="roof_photos",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(_("Roof photo"), upload_to="quotes/roofs/")

    def __str__(self) -> str:
        return f"Roof photo #{self.pk}"


class TimeSlot(models.TextChoices):
    MORNING = "08:00-12:00", _("Morning (08:00–12:00)")
    AFTERNOON = "12:00-16:00", _("Afternoon (12:00–16:00)")
    EVENING = "16:00-19:00", _("Evening (16:00–19:00)")


class BookingStatus(models.TextChoices):
    REQUESTED = "requested", _("Requested")
    CONFIRMED = "confirmed", _("Confirmed")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")


class InspectionBooking(TimeStampedModel):
    """A request to book an on-site inspection."""

    full_name = models.CharField(_("Full name"), max_length=160)
    phone = models.CharField(_("Phone"), max_length=40)
    email = models.EmailField(_("Email"))
    address = models.TextField(_("Inspection address"))

    preferred_date = models.DateField(_("Preferred date"))
    time_slot = models.CharField(
        _("Preferred time"),
        max_length=20,
        choices=TimeSlot.choices,
        default=TimeSlot.MORNING,
    )
    notes = models.TextField(_("Additional notes"), blank=True)

    locale = models.CharField(_("Locale"), max_length=5, default="de")
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.REQUESTED,
    )

    class Meta:
        verbose_name = _("Inspection booking")
        verbose_name_plural = _("Inspection bookings")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.full_name} — {self.preferred_date} {self.time_slot}"
