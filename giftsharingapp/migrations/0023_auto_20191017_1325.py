# Generated by Django 2.1.3 on 2019-10-17 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0022_notificationactionbutton'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationactionbutton',
            name='notification',
        ),
        migrations.AddField(
            model_name='notification',
            name='action_link',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
        migrations.DeleteModel(
            name='NotificationActionButton',
        ),
    ]
