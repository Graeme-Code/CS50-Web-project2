# Generated by Django 3.0.8 on 2020-07-22 09:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20200722_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='imageURL',
            field=models.URLField(null=True, validators=[django.core.validators.URLValidator]),
        ),
    ]
