# Generated by Django 3.0.8 on 2020-07-22 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200722_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=64),
        ),
    ]
