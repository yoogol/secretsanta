# Generated by Django 2.1.3 on 2018-12-12 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('giftsharingapp', '0015_auto_20181206_2143'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend_email', models.EmailField(max_length=200)),
                ('message', models.TextField(blank=True, max_length=2000, null=True)),
                ('date_invited', models.DateTimeField(auto_now_add=True)),
                ('inviter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
