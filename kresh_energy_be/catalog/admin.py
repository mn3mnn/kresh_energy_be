from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import FAQ
from .models import CalculatorConfig
from .models import Project
from .models import Service
from .models import ServiceArea
from .models import Testimonial


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title_de", "audience", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["audience", "is_active"]
    search_fields = [
        "title_de",
        "title_en",
        "title_ar",
        "summary_de",
        "summary_en",
        "summary_ar",
    ]
    prepopulated_fields = {"slug": ("title_de",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title_de",
        "city",
        "size_kwp",
        "panel_count",
        "is_featured",
        "is_active",
    ]
    list_editable = ["is_featured", "is_active"]
    list_filter = ["audience", "is_featured", "is_active", "city"]
    search_fields = ["title_de", "title_en", "title_ar", "city"]
    prepopulated_fields = {"slug": ("title_de",)}
    readonly_fields = ["image_preview"]

    @admin.display(description=_("Preview"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:160px;border-radius:8px;" />',
                obj.image.url,
            )
        return "—"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question_de", "category", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = [
        "question_de",
        "question_en",
        "question_ar",
        "answer_de",
        "answer_en",
        "answer_ar",
    ]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["author_name", "city", "rating", "is_featured", "is_active"]
    list_editable = ["is_featured", "is_active"]
    list_filter = ["rating", "is_featured", "is_active"]
    search_fields = ["author_name", "city", "quote_de", "quote_en", "quote_ar"]


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "postal_code", "contact_phone", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "postal_code"]


@admin.register(CalculatorConfig)
class CalculatorConfigAdmin(admin.ModelAdmin):
    """Single editable record of solar-calculator assumptions."""

    fieldsets = (
        (
            _("Production"),
            {"fields": ("specific_yield", "panel_kwp", "panel_area_m2")},
        ),
        (
            _("Consumption"),
            {
                "fields": (
                    "base_consumption",
                    "per_member_consumption",
                    "ev_consumption",
                ),
            },
        ),
        (
            _("Self-consumption"),
            {
                "fields": (
                    "self_consumption_no_battery",
                    "self_consumption_with_battery",
                ),
            },
        ),
        (
            _("Usable-roof factors"),
            {
                "fields": (
                    "usable_roof_factor_pitched",
                    "usable_roof_factor_flat",
                    "usable_roof_factor_other",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        # Singleton: only allow adding when no row exists yet.
        return not CalculatorConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the one-row list and jump straight to the singleton's edit page.
        obj = CalculatorConfig.get_instance()
        return redirect(
            reverse("admin:catalog_calculatorconfig_change", args=[obj.pk]),
        )
