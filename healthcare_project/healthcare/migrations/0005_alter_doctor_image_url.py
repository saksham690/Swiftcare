# Generated by Django 5.2 on 2025-04-16 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0004_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='image_url',
            field=models.URLField(),
        ),
    ]
