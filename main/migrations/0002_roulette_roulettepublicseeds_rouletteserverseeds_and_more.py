# Generated by Django 4.0.2 on 2022-05-19 16:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roulette',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('win', models.IntegerField()),
                ('roll_color', models.CharField(max_length=32)),
                ('round_number', models.IntegerField(default=0, unique=True)),
                ('is_over', models.BooleanField(default=False)),
                ('round_start_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoulettePublicSeeds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_seed', models.CharField(default='asd', max_length=32)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouletteServerSeeds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_seed', models.CharField(default='adss', max_length=64)),
                ('hashed_server_seed', models.CharField(default='sdadads', max_length=64)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouletteBets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bet_value', models.IntegerField()),
                ('bet_choice', models.CharField(max_length=32)),
                ('bet_time', models.DateTimeField(auto_now_add=True)),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roulette_round', to='main.roulette')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roulette_bet_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='roulette',
            name='used_public_seed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roulette_used_public_seed', to='main.roulettepublicseeds'),
        ),
        migrations.AddField(
            model_name='roulette',
            name='used_server_seed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roulette_used_server_seed', to='main.rouletteserverseeds'),
        ),
    ]