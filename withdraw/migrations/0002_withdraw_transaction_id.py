# Generated by Django 4.0.2 on 2022-04-01 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('withdraw', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdraw',
            name='transaction_id',
            field=models.CharField(default='test12321sadasdadwteetadasdasdad', max_length=128),
            preserve_default=False,
        ),
    ]
