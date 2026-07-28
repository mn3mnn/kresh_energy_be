from django.contrib import admin

from kresh_energy_be.referrals.models import RedemptionRequest

from .models import InspectionBooking
from .models import QuoteRequest
from .models import QuoteRoofPhoto


class QuoteRoofPhotoInline(admin.TabularInline):
    model = QuoteRoofPhoto
    extra = 0


class RedemptionRequestInline(admin.TabularInline):
    model = RedemptionRequest
    fk_name = "quote_request"
    extra = 0
    fields = ["user", "amount_requested", "status", "created"]
    readonly_fields = ["user", "amount_requested", "created"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "email", "status", "created"]
    list_editable = ["status"]
    list_filter = ["status", "wants_battery", "wants_ev_charger", "created"]
    search_fields = ["full_name", "phone", "email", "address"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
    inlines = [QuoteRoofPhotoInline, RedemptionRequestInline]


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
