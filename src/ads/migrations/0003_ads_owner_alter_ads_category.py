# Generated by Django 5.2 on 2025-05-07 13:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_rename_product_ads'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ads',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='abs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ads',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='ads.category', verbose_name='Категории'),
        ),
    ]
