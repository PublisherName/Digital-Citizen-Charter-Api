# Generated by Django 5.0.3 on 2024-04-25 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0009_alter_organization_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='designation',
            name='allow_multiple',
            field=models.BooleanField(default=False),
        ),
    ]