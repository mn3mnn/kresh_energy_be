from django.db import migrations

OPERATIONS_GROUP_NAME = "Operations"

OPERATIONS_PERMISSIONS = [
    ("leads", "view_quoterequest"),
    ("leads", "change_quoterequest"),
    ("leads", "view_inspectionbooking"),
    ("leads", "change_inspectionbooking"),
    ("referrals", "view_referral"),
    ("referrals", "view_referraldiscount"),
    ("referrals", "view_referralrewardsettings"),
]


def create_operations_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

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
