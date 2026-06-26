from django.contrib import admin
from django.utils.html import format_html

from .models import FAQ
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

    @admin.display(description="Preview")
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
