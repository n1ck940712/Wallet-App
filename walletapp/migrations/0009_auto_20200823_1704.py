# Generated by Django 3.0.7 on 2020-08-23 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walletapp', '0008_auto_20200823_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbaccount',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='dbcategory',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
