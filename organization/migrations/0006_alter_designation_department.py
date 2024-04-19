# Generated by Django 5.0.3 on 2024-04-14 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_alter_designation_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='designation',
            name='department',
            field=models.ForeignKey(limit_choices_to={'organization_id': models.F('organization')}, on_delete=django.db.models.deletion.CASCADE, to='organization.department'),
        ),
    ]
