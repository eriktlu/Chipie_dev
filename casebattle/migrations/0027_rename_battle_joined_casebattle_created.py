# Generated by Django 4.0.2 on 2022-07-21 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casebattle', '0026_merge_20220713_1249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='casebattle',
            old_name='battle_joined',
            new_name='created',
        ),
    ]
