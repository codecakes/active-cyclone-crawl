# Generated by Django 3.0.7 on 2020-11-08 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cyclone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('region', models.CharField(max_length=120)),
                ('img_src', models.URLField(blank=True)),
                ('link_page', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synoptic_time', models.DateTimeField()),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('intensity', models.IntegerField(default=0)),
                ('cyclone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='snapshots', to='cyclones.Cyclone')),
            ],
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecast_hr', models.IntegerField(default=0)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('intensity', models.IntegerField(default=0)),
                ('forecast_time', models.DateTimeField()),
                ('cyclone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forecasts', to='cyclones.Cyclone')),
            ],
        ),
        migrations.AddConstraint(
            model_name='historicsnapshot',
            constraint=models.UniqueConstraint(fields=('synoptic_time', 'cyclone'), name='uniq_synoptic_time_cyclone_fkey'),
        ),
        migrations.AddConstraint(
            model_name='forecast',
            constraint=models.UniqueConstraint(fields=('forecast_time', 'lat', 'lng', 'forecast_hr', 'intensity', 'cyclone'), name='uniq_forecast_time_forecast_hr_cyclone_fkey'),
        ),
    ]
