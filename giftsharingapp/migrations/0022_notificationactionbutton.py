# Generated by Django 2.1.3 on 2019-10-17 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0021_auto_20191017_0055'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationActionButton',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_text', models.TextField(max_length=100)),
                ('action_url', models.TextField(max_length=10000)),
                ('bootstrap_class', models.TextField(blank=True, max_length=100, null=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_buttons', to='giftsharingapp.Notification')),
            ],
        ),
    ]