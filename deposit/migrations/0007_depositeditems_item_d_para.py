# Generated by Django 4.0.2 on 2022-04-05 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit', '0006_depositeditems_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositeditems',
            name='item_d_para',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
