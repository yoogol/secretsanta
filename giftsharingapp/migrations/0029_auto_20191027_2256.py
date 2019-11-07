# Generated by Django 2.1.3 on 2019-10-28 02:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0028_auto_20191022_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendinvite',
            name='invited_to_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups_invitations', to='giftsharingapp.GifterGroup'),
        ),
        migrations.AlterField(
            model_name='friendinvite',
            name='sent_by_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_sent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='friendinvite',
            name='sent_to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_received', to=settings.AUTH_USER_MODEL),
        ),
    ]