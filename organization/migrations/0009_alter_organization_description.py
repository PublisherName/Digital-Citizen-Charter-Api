# Generated by Django 5.0.3 on 2024-04-22 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_alter_designation_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=models.TextField(),
        ),
    ]