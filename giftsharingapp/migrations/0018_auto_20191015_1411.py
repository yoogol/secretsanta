# Generated by Django 2.1.3 on 2019-10-15 18:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0017_auto_20191015_1300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='friendinvite',
            new_name='accepted_friendinvite',
        ),
        migrations.AlterField(
            model_name='friendinvite',
            name='sent_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitation_sent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='friendinvite',
            name='sent_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitation_received', to=settings.AUTH_USER_MODEL),
        ),
    ]
