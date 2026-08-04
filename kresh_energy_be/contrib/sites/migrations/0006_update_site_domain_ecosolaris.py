"""
Domain migration: energy.kresh-ng.de -> ecosolaris.kresh-ng.de. See
0003_set_site_domain_and_name.py for why this app/migration pattern exists.
"""
from django.conf import settings
from django.db import migrations


def update_site_domain(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(id=settings.SITE_ID).update(domain="ecosolaris.kresh-ng.de")


def revert_site_domain(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(id=settings.SITE_ID).update(domain="energy.kresh-ng.de")


class Migration(migrations.Migration):

    dependencies = [("sites", "0005_update_site_domain")]

    operations = [migrations.RunPython(update_site_domain, revert_site_domain)]
