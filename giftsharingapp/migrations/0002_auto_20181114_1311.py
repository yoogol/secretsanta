# Generated by Django 2.1.3 on 2018-11-14 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftsharingapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gift',
            name='date_saved',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='gift',
            name='description',
            field=models.TextField(help_text='Describe your desired gift', max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='gift',
            name='desirability_rank',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='gift',
            name='filled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gift',
            name='link',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='gift',
            name='price',
            field=models.IntegerField(null=True),
        ),
    ]
