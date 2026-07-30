from decimal import Decimal
from decimal import InvalidOperation

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .emails import render_quote_price_email_body
from .emails import send_quote_price_email_text
from .models import InspectionBooking
from .models import LeadStatus
from .models import QuoteRequest
from .models import QuoteRoofPhoto


class QuoteRoofPhotoInline(admin.TabularInline):
    model = QuoteRoofPhoto
    extra = 0


class SendQuoteForm(forms.Form):
    quoted_price = forms.DecimalField(
        label=_("Quoted price (€)"),
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    email_body = forms.CharField(
        label=_("Email content"),
        widget=forms.Textarea(
            attrs={"rows": 20, "style": "width: 100%; font-family: monospace;"},
        ),
    )


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "email", "status", "quoted_price", "created"]
    list_editable = ["status"]
    list_filter = ["status", "wants_battery", "wants_ev_charger", "created"]
    search_fields = ["full_name", "phone", "email", "address"]
    date_hierarchy = "created"
    readonly_fields = [
        "created",
        "modified",
        "discount_reminder",
        "quoted_price",
        "quoted_price_sent_at",
    ]
    inlines = [QuoteRoofPhotoInline]
    change_form_template = "admin/leads/quoterequest/change_form.html"

    # Non-superuser staff (the "Operations" group) may only change status
    # directly — quoted_price is always set via the "Send quote" action
    # (see get_urls/send_quote_view below), never edited as a plain field.
    OPERATIONS_ONLY_READONLY_FIELDS = [
        "full_name",
        "phone",
        "email",
        "address",
        "notes",
        "calc_monthly_bill",
        "calc_system_size_kwp",
        "calc_roof_type",
        "wants_battery",
        "wants_ev_charger",
        "electricity_bill",
        "meter_photo",
        "submitted_by",
        "locale",
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and request.user.groups.filter(
            name="Operations",
        ).exists():
            readonly_fields += self.OPERATIONS_ONLY_READONLY_FIELDS
        return readonly_fields

    fieldsets = (
        (
            _("Contact"),
            {"fields": ("full_name", "phone", "email", "address", "notes")},
        ),
        (
            _("Calculator snapshot"),
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
            _("Files"),
            {"fields": ("electricity_bill", "meter_photo")},
        ),
        (
            _("Status"),
            {"fields": ("status", "submitted_by", "locale")},
        ),
        (
            _("Pricing"),
            {"fields": ("discount_reminder", "quoted_price", "quoted_price_sent_at")},
        ),
        (
            _("Metadata"),
            {"fields": ("created", "modified")},
        ),
    )

    @admin.display(description=_("Referral discount to account for"))
    def discount_reminder(self, obj):
        if not obj.pk:
            return _("None")
        discount = obj.applied_referral_discount.first()
        if not discount:
            return _("None")
        return _(
            "€%(amount)s (voucher #%(pk)s, owner: %(email)s) "
            "— NOT auto-subtracted, factor manually into quoted_price.",
        ) % {
            "amount": discount.amount,
            "pk": discount.pk,
            "email": discount.owner.email,
        }

    def get_urls(self):
        custom_urls = [
            path(
                "<path:object_id>/send-quote/",
                self.admin_site.admin_view(self.send_quote_view),
                name="leads_quoterequest_send_quote",
            ),
        ]
        return custom_urls + super().get_urls()

    def send_quote_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj is None:
            raise Http404
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if request.method == "POST":
            if "_refresh" in request.POST:
                preview_price = self._parse_price(
                    request.POST.get("quoted_price"),
                    fallback=obj.quoted_price,
                )
                form = SendQuoteForm(
                    initial={
                        "quoted_price": preview_price,
                        "email_body": render_quote_price_email_body(
                            obj,
                            preview_price,
                        ),
                    },
                )
            else:
                form = SendQuoteForm(request.POST)
                if form.is_valid():
                    send_quote_price_email_text(obj, form.cleaned_data["email_body"])
                    obj.quoted_price = form.cleaned_data["quoted_price"]
                    obj.quoted_price_sent_at = timezone.now()
                    obj.status = LeadStatus.QUOTED
                    obj.save(
                        update_fields=[
                            "quoted_price",
                            "quoted_price_sent_at",
                            "status",
                        ],
                    )
                    self.message_user(
                        request,
                        _("Priced quote email sent to %(email)s.")
                        % {"email": obj.email},
                    )
                    return redirect(
                        reverse("admin:leads_quoterequest_change", args=[obj.pk]),
                    )
        else:
            preview_price = obj.quoted_price or Decimal("0")
            form = SendQuoteForm(
                initial={
                    "quoted_price": obj.quoted_price,
                    "email_body": render_quote_price_email_body(obj, preview_price),
                },
            )

        context = {
            **self.admin_site.each_context(request),
            "title": _("Send quote"),
            "object": obj,
            "opts": self.model._meta,
            "form": form,
        }
        return TemplateResponse(
            request,
            "admin/leads/quoterequest/send_quote.html",
            context,
        )

    @staticmethod
    def _parse_price(raw_value, fallback):
        if raw_value:
            try:
                return Decimal(str(raw_value).replace(",", "."))
            except (InvalidOperation, ValueError):
                pass
        return fallback or Decimal("0")


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
