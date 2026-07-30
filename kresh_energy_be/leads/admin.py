from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from .emails import send_quote_price_email
from .models import InspectionBooking
from .models import LeadStatus
from .models import QuoteRequest
from .models import QuoteRoofPhoto


class QuoteRoofPhotoInline(admin.TabularInline):
    model = QuoteRoofPhoto
    extra = 0


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "email", "status", "created"]
    list_editable = ["status"]
    list_filter = ["status", "wants_battery", "wants_ev_charger", "created"]
    search_fields = ["full_name", "phone", "email", "address"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified", "discount_reminder"]
    inlines = [QuoteRoofPhotoInline]
    change_form_template = "admin/leads/quoterequest/change_form.html"

    fieldsets = (
        (
            "Contact",
            {"fields": ("full_name", "phone", "email", "address", "notes")},
        ),
        (
            "Calculator snapshot",
            {
                "fields": (
                    "calc_monthly_bill",
                    "calc_system_size_kwp",
                    "calc_roof_type",
                    "wants_battery",
                    "wants_ev_charger",
                ),
            },
        ),
        (
            "Files",
            {"fields": ("electricity_bill", "meter_photo")},
        ),
        (
            "Status",
            {"fields": ("status", "submitted_by", "locale")},
        ),
        (
            "Pricing",
            {"fields": ("discount_reminder", "quoted_price", "quoted_price_sent_at")},
        ),
        (
            "Metadata",
            {"fields": ("created", "modified")},
        ),
    )

    @admin.display(description="Referral discount to account for")
    def discount_reminder(self, obj):
        if not obj.pk:
            return "None"
        discount = obj.applied_referral_discount.first()
        if not discount:
            return "None"
        return (
            f"€{discount.amount} (voucher #{discount.pk}, owner: {discount.owner.email}) "
            "— NOT auto-subtracted, factor manually into quoted_price."
        )

    def response_change(self, request, obj):
        if "_send_quote_email" in request.POST:
            if not obj.quoted_price:
                self.message_user(
                    request,
                    "Set a quoted price before sending.",
                    level=messages.ERROR,
                )
                return redirect(request.path)
            send_quote_price_email(obj, obj.quoted_price)
            obj.quoted_price_sent_at = timezone.now()
            obj.status = LeadStatus.QUOTED
            obj.save(update_fields=["quoted_price_sent_at", "status"])
            self.message_user(request, f"Priced quote email sent to {obj.email}.")
            return redirect(request.path)
        return super().response_change(request, obj)


@admin.register(InspectionBooking)
class InspectionBookingAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "phone",
        "preferred_date",
        "time_slot",
        "status",
        "created",
    ]
    list_editable = ["status"]
    list_filter = ["status", "time_slot", "preferred_date"]
    search_fields = ["full_name", "phone", "email", "address"]
    date_hierarchy = "preferred_date"
    readonly_fields = ["created", "modified"]
