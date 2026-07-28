from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import CreditEntryType
from .models import Referral
from .models import ReferralCredit
from .models import ReferralRewardSettings
from .models import RedemptionRequest
from .models import RedemptionRequestStatus


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


@admin.register(ReferralCredit)
class ReferralCreditAdmin(admin.ModelAdmin):
    list_display = ["user", "entry_type", "amount", "referral", "created"]
    list_filter = ["entry_type", "created"]
    search_fields = ["user__email"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]


@admin.register(RedemptionRequest)
class RedemptionRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "amount_requested", "quote_request", "status", "created"]
    list_editable = ["status"]
    list_filter = ["status", "created"]
    search_fields = ["user__email"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
    actions = ["mark_applied"]

    @admin.action(description="Mark applied (creates a REDEEMED ledger entry)")
    def mark_applied(self, request, queryset):
        applied = 0
        for redemption in queryset.filter(status=RedemptionRequestStatus.PENDING):
            ReferralCredit.objects.create(
                user=redemption.user,
                entry_type=CreditEntryType.REDEEMED,
                amount=redemption.amount_requested,
                note=f"Redemption request #{redemption.pk} applied by {request.user}.",
            )
            redemption.status = RedemptionRequestStatus.APPLIED
            redemption.save(update_fields=["status"])
            applied += 1
        self.message_user(request, f"Marked {applied} redemption request(s) as applied.")
