# Generated by Django 4.2.11 on 2024-05-09 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_is_active_activationkey"),
    ]

    operations = [
        migrations.RenameField(
            model_name="activationkey",
            old_name="key",
            new_name="activation_keys",
        ),
    ]
