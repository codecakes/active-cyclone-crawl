# Generated by Django 3.0.7 on 2020-11-12 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyclones', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cyclone',
            constraint=models.UniqueConstraint(fields=('name', 'region'), name='uniq_name_region'),
        ),
    ]