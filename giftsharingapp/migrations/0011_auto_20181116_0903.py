# Generated by Django 2.1.3 on 2018-11-16 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0010_auto_20181116_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='gifter_groups',
            field=models.ManyToManyField(to='giftsharingapp.GifterGroup'),
        ),
    ]
