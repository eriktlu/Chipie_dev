from django.db import models

from main.models import CustomUser

class Withdraw(models.Model):
    steam_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="withdraw_user")
    transaction_value_crypto = models.DecimalField(max_digits=16, decimal_places=10)
    crypto_type = models.CharField(max_length=10)
    transaction_value_gold = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=128)
    country_code = models.CharField(max_length=4, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return str(self.created)
