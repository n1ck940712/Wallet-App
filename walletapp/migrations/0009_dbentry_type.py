# Generated by Django 3.0.7 on 2020-07-05 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walletapp', '0008_auto_20200705_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbentry',
            name='type',
            field=models.CharField(default='null', max_length=64),
            preserve_default=False,
        ),
    ]