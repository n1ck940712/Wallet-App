# Generated by Django 3.0.7 on 2020-08-23 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walletapp', '0006_myuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='first_name',
            field=models.CharField(default='first', max_length=255, verbose_name='first name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='myuser',
            name='last_name',
            field=models.CharField(default='last', max_length=255, verbose_name='last name'),
            preserve_default=False,
        ),
    ]
