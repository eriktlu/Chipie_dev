# Generated by Django 4.0.2 on 2022-05-05 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casebattle', '0017_alter_casebattle_battle_result_coins'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebattle',
            name='room_seat',
            field=models.IntegerField(default=0),
        ),
    ]
