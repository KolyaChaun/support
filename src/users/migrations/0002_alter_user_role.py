from django.db import migrations, models
from users.enums import Role

class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("senior", "Senior"),
                    ("junior", "Junior"),
                ],
                default=Role.JUNIOR.value,  # Accessing enum value
                max_length=15,
            ),
        ),
    ]
