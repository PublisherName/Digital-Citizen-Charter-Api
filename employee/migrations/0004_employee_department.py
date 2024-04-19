# Generated by Django 5.0.3 on 2024-04-19 08:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_alter_employee_designation'),
        ('organization', '0008_alter_designation_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='organization.department'),
            preserve_default=False,
        ),
    ]
