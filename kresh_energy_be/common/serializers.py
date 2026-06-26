"""Shared serializer helpers."""

from __future__ import annotations

from django.utils.translation import get_language
from rest_framework import serializers

DEFAULT_LANGUAGE = "de"
SUPPORTED_LANGUAGES = ("de", "en", "ar")


def resolve_language() -> str:
    """Return the active 2-letter language, falling back to the default."""
    lang = (get_language() or DEFAULT_LANGUAGE)[:2]
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


class TranslatedFieldsMixin(serializers.Serializer):
    """Expose ``<field>_<lang>`` model columns as a single ``<field>`` key.

    Declare the base field names in ``translated_fields``. The active request
    language (set by ``LocaleMiddleware`` from the ``Accept-Language`` header) is
    used to pick the value, falling back to the default language when empty.
    """

    translated_fields: tuple[str, ...] = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = resolve_language()
        for field in self.translated_fields:
            value = getattr(instance, f"{field}_{lang}", "") or getattr(
                instance,
                f"{field}_{DEFAULT_LANGUAGE}",
                "",
            )
            data[field] = value
        return data
