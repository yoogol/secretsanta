# Generated by Django 2.1.3 on 2018-11-16 03:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0007_giftergroup_userinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_info', to=settings.AUTH_USER_MODEL),
        ),
    ]
