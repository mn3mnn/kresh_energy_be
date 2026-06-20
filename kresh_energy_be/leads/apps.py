from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LeadsConfig(AppConfig):
    name = "kresh_energy_be.leads"
    verbose_name = _("Leads")
