# Generated by Django 5.0.3 on 2024-07-09 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0011_remove_employee_profile_picture_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
