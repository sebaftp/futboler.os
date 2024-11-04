# Generated by Django 5.1.2 on 2024-11-04 21:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20241028_0024'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='id_group',
            new_name='id',
        ),
        migrations.AlterField(
            model_name='group',
            name='banner',
            field=models.ImageField(default='default_banner.png', upload_to='group_banners'),
        ),
        migrations.AlterField(
            model_name='group',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='group_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='group',
            name='logo',
            field=models.ImageField(default='default_logo.png', upload_to='group_logos'),
        ),
    ]