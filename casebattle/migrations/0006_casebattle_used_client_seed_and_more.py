# Generated by Django 4.0.2 on 2022-05-02 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('casebattle', '0005_delete_seeds'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebattle',
            name='used_client_seed',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='casebattle_client_seed', to='casebattle.casebattleclientseed'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='casebattle',
            name='used_server_seed',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='casebattle_server_seed', to='casebattle.casebattleserverseed'),
            preserve_default=False,
        ),
    ]
