# Generated by Django 5.0.3 on 2024-04-26 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_rename_description_employee_remarks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='remarks',
            new_name='description',
        ),
    ]
