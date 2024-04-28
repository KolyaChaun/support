from django.db import migrations, models 

import users.enums 




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
                default=users.enums.Role["JUNIOR"],
                max_length=15,
            ),
        ),
    ]
