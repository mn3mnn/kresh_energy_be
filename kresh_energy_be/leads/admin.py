from django.contrib import admin

from .models import InspectionBooking
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
    readonly_fields = ["created", "modified"]
    inlines = [QuoteRoofPhotoInline]


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
