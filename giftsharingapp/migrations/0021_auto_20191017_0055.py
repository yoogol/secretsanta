# Generated by Django 2.1.3 on 2019-10-17 04:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0020_auto_20191016_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='owner',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userinfo', to=settings.AUTH_USER_MODEL),
        ),
    ]
