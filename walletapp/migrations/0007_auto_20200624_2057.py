# Generated by Django 3.0.7 on 2020-06-24 12:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('walletapp', '0006_auto_20200622_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbentry',
            name='entryNote',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='dbentry',
            name='entryDate',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='dbentry',
            name='entryTime',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
    ]
