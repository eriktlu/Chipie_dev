# Generated by Django 4.0.2 on 2022-07-21 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_bet_time_roulettebets_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='roulettebets',
            name='game',
            field=models.CharField(default='roulette', max_length=128),
        ),
    ]
