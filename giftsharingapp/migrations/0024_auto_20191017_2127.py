# Generated by Django 2.1.3 on 2019-10-18 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0023_auto_20191017_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendinvite',
            name='date_declined',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='friendinvite',
            name='declined',
            field=models.BooleanField(default=False),
        ),
    ]