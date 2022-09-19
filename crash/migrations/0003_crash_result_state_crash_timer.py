# Generated by Django 4.0.2 on 2022-05-14 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0002_crash_over'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='result_state',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='crash',
            name='timer',
            field=models.DecimalField(decimal_places=1, default=30.0, max_digits=4),
        ),
    ]