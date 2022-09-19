# Generated by Django 4.0.2 on 2022-07-21 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('casebattle', '0028_casebattle_game_casebattle_total_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casebattle',
            name='used_hashed_server_seed',
        ),
        migrations.RemoveField(
            model_name='casebattle',
            name='used_server_seed',
        ),
        migrations.AddField(
            model_name='casebattleroom',
            name='used_server_seed',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='casebattle_used_server_seed', to='casebattle.casebattleserverseed'),
        ),
    ]