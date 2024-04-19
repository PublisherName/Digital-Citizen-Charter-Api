# Generated by Django 5.0.3 on 2024-04-14 17:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_employee_organization'),
        ('organization', '0008_alter_designation_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='designation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.designation'),
        ),
    ]
