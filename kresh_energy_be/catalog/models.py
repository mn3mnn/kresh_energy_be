from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class AudienceChoices(models.TextChoices):
    RESIDENTIAL = "residential", _("Residential")
    COMMERCIAL = "commercial", _("Commercial")
    BOTH = "both", _("Residential & Commercial")


class Service(TimeStampedModel):
    """A solar-energy service offered by Kresh Energy."""

    slug = models.SlugField(_("Slug"), unique=True, max_length=120)
    icon = models.CharField(
        _("Icon"),
        max_length=50,
        blank=True,
        help_text=_("lucide-react icon name, e.g. 'sun-medium'."),
    )
    audience = models.CharField(
        _("Audience"),
        max_length=20,
        choices=AudienceChoices.choices,
        default=AudienceChoices.BOTH,
    )
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    title_de = models.CharField(_("Title (DE)"), max_length=160)
    title_en = models.CharField(_("Title (EN)"), max_length=160, blank=True)
    title_ar = models.CharField(_("Title (AR)"), max_length=160, blank=True)
    summary_de = models.CharField(_("Summary (DE)"), max_length=280)
    summary_en = models.CharField(_("Summary (EN)"), max_length=280, blank=True)
    summary_ar = models.CharField(_("Summary (AR)"), max_length=280, blank=True)
    description_de = models.TextField(_("Description (DE)"), blank=True)
    description_en = models.TextField(_("Description (EN)"), blank=True)
    description_ar = models.TextField(_("Description (AR)"), blank=True)
    body_de = models.TextField(
        _("Body (DE)"),
        blank=True,
        help_text=_(
            "Long-form landing-page content. Separate paragraphs with a blank line.",
        ),
    )
    body_en = models.TextField(_("Body (EN)"), blank=True)
    body_ar = models.TextField(_("Body (AR)"), blank=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title_de


class Project(TimeStampedModel):
    """A completed installation shown in the portfolio."""

    slug = models.SlugField(_("Slug"), unique=True, max_length=140)
    city = models.CharField(_("City"), max_length=120)
    size_kwp = models.DecimalField(
        _("System size (kWp)"),
        max_digits=7,
        decimal_places=2,
    )
    panel_count = models.PositiveIntegerField(_("Number of panels"), default=0)
    image = models.ImageField(_("Image"), upload_to="projects/", blank=True)
    date_completed = models.DateField(_("Completed on"), null=True, blank=True)
    audience = models.CharField(
        _("Audience"),
        max_length=20,
        choices=AudienceChoices.choices,
        default=AudienceChoices.RESIDENTIAL,
    )
    is_featured = models.BooleanField(_("Featured"), default=False)
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    title_de = models.CharField(_("Title (DE)"), max_length=180)
    title_en = models.CharField(_("Title (EN)"), max_length=180, blank=True)
    title_ar = models.CharField(_("Title (AR)"), max_length=180, blank=True)
    description_de = models.TextField(_("Description (DE)"), blank=True)
    description_en = models.TextField(_("Description (EN)"), blank=True)
    description_ar = models.TextField(_("Description (AR)"), blank=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["order", "-date_completed", "id"]

    def __str__(self) -> str:
        return f"{self.title_de} — {self.city}"


class FAQCategory(models.TextChoices):
    GENERAL = "general", _("General")
    INSTALLATION = "installation", _("Installation")
    WARRANTY = "warranty", _("Warranty")
    MAINTENANCE = "maintenance", _("Maintenance")
    BATTERY = "battery", _("Battery & storage")
    CONSUMPTION = "consumption", _("Energy consumption")
    PERMITS = "permits", _("Permits & approvals")
    TECHNICAL = "technical", _("Technical")


class FAQ(TimeStampedModel):
    """A frequently asked question."""

    category = models.CharField(
        _("Category"),
        max_length=20,
        choices=FAQCategory.choices,
        default=FAQCategory.GENERAL,
    )
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    question_de = models.CharField(_("Question (DE)"), max_length=255)
    question_en = models.CharField(_("Question (EN)"), max_length=255, blank=True)
    question_ar = models.CharField(_("Question (AR)"), max_length=255, blank=True)
    answer_de = models.TextField(_("Answer (DE)"))
    answer_en = models.TextField(_("Answer (EN)"), blank=True)
    answer_ar = models.TextField(_("Answer (AR)"), blank=True)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ["category", "order", "id"]

    def __str__(self) -> str:
        return self.question_de


class Testimonial(TimeStampedModel):
    """A customer testimonial."""

    author_name = models.CharField(_("Author name"), max_length=120)
    city = models.CharField(_("City"), max_length=120, blank=True)
    rating = models.PositiveSmallIntegerField(_("Rating"), default=5)
    avatar = models.ImageField(_("Avatar"), upload_to="testimonials/", blank=True)
    is_featured = models.BooleanField(_("Featured"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    role_de = models.CharField(_("Role (DE)"), max_length=120, blank=True)
    role_en = models.CharField(_("Role (EN)"), max_length=120, blank=True)
    role_ar = models.CharField(_("Role (AR)"), max_length=120, blank=True)
    quote_de = models.TextField(_("Quote (DE)"))
    quote_en = models.TextField(_("Quote (EN)"), blank=True)
    quote_ar = models.TextField(_("Quote (AR)"), blank=True)

    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.author_name


class ServiceArea(TimeStampedModel):
    """A city/region Kresh Energy serves (also feeds the future coverage map)."""

    name = models.CharField(_("City / region"), max_length=120)
    postal_code = models.CharField(_("Postal code"), max_length=12, blank=True)
    latitude = models.DecimalField(
        _("Latitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        _("Longitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    contact_phone = models.CharField(_("Contact phone"), max_length=40, blank=True)
    contact_email = models.EmailField(_("Contact email"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Service area")
        verbose_name_plural = _("Service areas")
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class CalculatorConfig(TimeStampedModel):
    """Admin-editable assumptions for the solar calculator (singleton, pk=1).

    Mirrors the constants the frontend ships as defaults (``solar.ts``); editing
    these here lets staff tune the estimator without a code deploy.
    """

    # Tariffs
    electricity_price = models.DecimalField(
        _("Electricity price (€/kWh)"),
        max_digits=6,
        decimal_places=3,
        default=0.350,
        help_text=_("German household average, e.g. 0.350."),
    )
    feed_in_tariff = models.DecimalField(
        _("Feed-in tariff (€/kWh)"),
        max_digits=6,
        decimal_places=3,
        default=0.080,
        help_text=_("Paid for surplus fed into the grid."),
    )

    # Production
    specific_yield = models.PositiveIntegerField(
        _("Specific yield (kWh/kWp·yr)"),
        default=950,
        help_text=_("Annual yield per kWp in Germany."),
    )
    panel_kwp = models.DecimalField(
        _("Panel power (kWp)"),
        max_digits=5,
        decimal_places=3,
        default=0.430,
        help_text=_("Per-module peak power, e.g. 0.430 for a 430 Wp module."),
    )
    panel_area_m2 = models.DecimalField(
        _("Panel area (m²)"),
        max_digits=5,
        decimal_places=2,
        default=1.85,
        help_text=_("Usable area per module incl. framing."),
    )

    # Consumption
    base_consumption = models.PositiveIntegerField(
        _("Base consumption (kWh/yr)"),
        default=1500,
        help_text=_("Household base load before per-member additions."),
    )
    per_member_consumption = models.PositiveIntegerField(
        _("Per-member consumption (kWh/yr)"),
        default=900,
    )
    ev_consumption = models.PositiveIntegerField(
        _("EV consumption (kWh/yr)"),
        default=2500,
        help_text=_("Added when the customer wants an EV charger."),
    )

    # Self-consumption rates (share of production used on site)
    self_consumption_no_battery = models.DecimalField(
        _("Self-consumption without battery"),
        max_digits=4,
        decimal_places=2,
        default=0.30,
        help_text=_("Fraction 0–1, e.g. 0.30."),
    )
    self_consumption_with_battery = models.DecimalField(
        _("Self-consumption with battery"),
        max_digits=4,
        decimal_places=2,
        default=0.65,
        help_text=_("Fraction 0–1, e.g. 0.65."),
    )

    # Usable-roof factors per roof type (share of roof area usable for panels)
    usable_roof_factor_pitched = models.DecimalField(
        _("Usable roof factor – pitched"),
        max_digits=4,
        decimal_places=2,
        default=0.75,
    )
    usable_roof_factor_flat = models.DecimalField(
        _("Usable roof factor – flat"),
        max_digits=4,
        decimal_places=2,
        default=0.50,
    )
    usable_roof_factor_other = models.DecimalField(
        _("Usable roof factor – other"),
        max_digits=4,
        decimal_places=2,
        default=0.60,
    )

    class Meta:
        verbose_name = _("Calculator configuration")
        verbose_name_plural = _("Calculator configuration")

    def __str__(self) -> str:
        return "Calculator configuration"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce a single row
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # The singleton is never deleted.
        pass

    @classmethod
    def get_instance(cls) -> "CalculatorConfig":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
