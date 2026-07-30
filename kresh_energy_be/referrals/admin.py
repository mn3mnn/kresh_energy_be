from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import Referral
from .models import ReferralDiscount
from .models import ReferralRewardSettings


@admin.register(ReferralRewardSettings)
class ReferralRewardSettingsAdmin(admin.ModelAdmin):
    """Single editable record of referral reward amounts."""

    fields = ["referrer_reward_amount", "referred_reward_amount", "is_active"]

    def has_add_permission(self, request):
        # Singleton: only allow adding when no row exists yet.
        return not ReferralRewardSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the one-row list and jump straight to the singleton's edit page.
        obj = ReferralRewardSettings.get_instance()
        return redirect(
            reverse("admin:referrals_referralrewardsettings_change", args=[obj.pk]),
        )


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = [
        "referrer",
        "referred_user",
        "status",
        "code_used",
        "rewarded_at",
        "created",
    ]
    list_filter = ["status", "created"]
    search_fields = ["referrer__email", "referred_user__email", "code_used"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]


@admin.register(ReferralDiscount)
class ReferralDiscountAdmin(admin.ModelAdmin):
    list_display = ["owner", "referral", "amount", "status", "quote_request", "applied_at", "created"]
    list_filter = ["status", "created"]
    search_fields = ["owner__email"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
