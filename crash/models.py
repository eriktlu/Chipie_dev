from django.db import models

from main.models import CustomUser

# Create your models here.

class CrashPublicSeeds(models.Model):
    public_seed = models.CharField(max_length=32)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.public_seed

class CrashServerSeeds(models.Model):
    server_seed = models.CharField(max_length=64)
    hashed_server_seed = models.CharField(max_length=64)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.server_seed
    

class Crash(models.Model):
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    result_state = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)

    round_number = models.IntegerField(default = 0, unique=True)

    over = models.BooleanField(default=False)
    timer = models.DecimalField(max_digits=4, decimal_places=1, default=20.0)

    used_server_seed = models.ForeignKey(CrashServerSeeds, on_delete=models.CASCADE, related_name="crash_used_server_seed")

    used_public_seed = models.ForeignKey(CrashPublicSeeds, on_delete=models.CASCADE, related_name="crash_used_public_seed")
    
    round_start_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.round_number)

class CrashBets(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="crash_user")
    crash_round = models.ForeignKey(Crash, on_delete=models.CASCADE, related_name="crash_round")

    bet_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    win = models.BooleanField(null=True, default=None)
    stop_point = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    bet_choice = models.CharField(max_length=100, null=True, default=None)

    game = models.CharField(max_length=128, default='crash')

    total_result = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username