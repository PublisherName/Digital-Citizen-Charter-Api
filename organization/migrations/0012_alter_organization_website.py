# Generated by Django 5.0.3 on 2024-07-10 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_rename_allow_multiple_designation_allow_multiple_employees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='website',
            field=models.URLField(),
        ),
    ]
