from django.db import models
from django.utils.timezone import utc
import datetime

from django.contrib.auth.models import AbstractUser
from django.forms import CharField

from .managers import CustomUserManager


# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField(max_length=32, blank=True, null=True)

    name = models.CharField(max_length=200, unique=True)

    steam_id = models.CharField(max_length=17, unique=True, blank=True, null=True, db_column='steam_id')
    player = models.TextField(null=True)
    user_coins = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    trade_link = models.CharField(max_length=256, blank=True)

    avatar = models.CharField(max_length=128, blank=True)

    client_seed = models.CharField(max_length=32, default='default')

    is_active = models.BooleanField(default=True, db_column='status')
    is_staff = models.BooleanField(default=False, db_column='isstaff')
    is_superuser = models.BooleanField(default=False, db_column='issuperuser')

    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Messages(models.Model):
    name = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class TradeOffers(models.Model):
    name = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    offer_id = models.CharField(max_length=150, unique=True)
    offer_state = models.IntegerField()
    offer_message = models.TextField(null=True)
    trade_id = models.CharField(max_length=150, unique=True, null=True)
    offer_value = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

class CsgoItems(models.Model):
    market_hash_name = models.CharField(max_length=200, unique=True)
    item_value = models.FloatField()
    border_color = models.CharField(max_length=100)


class RoulettePublicSeeds(models.Model):
    public_seed = models.CharField(max_length=32, default='asd')

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.public_seed

class RouletteServerSeeds(models.Model):
    server_seed = models.CharField(max_length=64, default='adss')
    hashed_server_seed = models.CharField(max_length=64, default='sdadads')

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.server_seed

class Roulette(models.Model):
    win = models.IntegerField()
    roll_color = models.CharField(max_length=32)

    round_number = models.IntegerField(default = 0, unique=True)
    

    used_server_seed = models.ForeignKey(RouletteServerSeeds, on_delete=models.CASCADE, related_name="roulette_used_server_seed")

    used_public_seed = models.ForeignKey(RoulettePublicSeeds, on_delete=models.CASCADE, related_name="roulette_used_public_seed")

    is_over = models.BooleanField(default=False)
    round_start_time = models.DateTimeField(auto_now_add=True)

    def get_time_diff(self):
        if self.round_start_time:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            timediff = now - self.round_start_time
            return timediff.total_seconds()

    def __str__(self):
        return str(self.round_number)

class RouletteBets(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="roulette_bet_user")
    round = models.ForeignKey(Roulette, on_delete=models.CASCADE, related_name="roulette_round")

    bet_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bet_choice = models.CharField(max_length=32)
    win = models.BooleanField(null=True, default=False)

    win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    game = models.CharField(max_length=128, default='roulette')

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


    
    