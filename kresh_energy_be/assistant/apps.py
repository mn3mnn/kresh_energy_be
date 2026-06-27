from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AssistantConfig(AppConfig):
    name = "kresh_energy_be.assistant"
    verbose_name = _("Assistant")
