# Generated by Django 5.0.3 on 2024-04-14 15:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='organization',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
            preserve_default=False,
        ),
    ]
