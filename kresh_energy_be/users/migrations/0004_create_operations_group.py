from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

OPERATIONS_GROUP_NAME = "Operations"

OPERATIONS_PERMISSIONS = [
    ("leads", "view_quoterequest"),
    ("leads", "change_quoterequest"),
    ("leads", "view_inspectionbooking"),
    ("leads", "change_inspectionbooking"),
    ("leads", "view_quoteroofphoto"),
    ("referrals", "view_referral"),
    ("referrals", "view_referraldiscount"),
    ("referrals", "view_referralrewardsettings"),
]


def create_operations_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Default add/change/delete/view permissions are normally created by the
    # post_migrate signal — but that only fires once, after every migration
    # in this *entire* `migrate` run has applied, not incrementally after
    # each app's own migrations. Since this migration runs mid-plan, the
    # leads/referrals permissions declared as dependencies above may not
    # exist in the database yet on a fresh database (e.g. CI). Force-create
    # them now via Django's real permission-creation routine — it needs the
    # actual app registry/model classes (not this migration's frozen
    # historical `apps`), since it inspects Meta.permissions/
    # default_permissions.
    using = schema_editor.connection.alias
    for app_label in {app_label for app_label, _codename in OPERATIONS_PERMISSIONS}:
        create_permissions(
            global_apps.get_app_config(app_label),
            verbosity=0,
            using=using,
        )

    group, _created = Group.objects.get_or_create(name=OPERATIONS_GROUP_NAME)

    permissions = []
    for app_label, codename in OPERATIONS_PERMISSIONS:
        permissions.append(
            Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            ),
        )
    group.permissions.set(permissions)


def remove_operations_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=OPERATIONS_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_phone"),
        ("leads", "0004_remove_quoterequest_redeem_credit_and_more"),
        ("referrals", "0002_remove_referralcredit_referral_and_more"),
    ]

    operations = [
        migrations.RunPython(create_operations_group, remove_operations_group),
    ]
