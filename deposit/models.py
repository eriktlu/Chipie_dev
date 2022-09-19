from decimal import Decimal
from django.utils.timezone import utc
import datetime

from django.db import models

from main.models import CustomUser

class Deposit(models.Model):
    steam_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="deposit_user")
    transaction_value_money = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_value_gold = models.DecimalField(max_digits=10, decimal_places=2)
    country_code = models.CharField(max_length=4, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    payment_option = models.CharField(max_length=200, blank=True)
    billing_status = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return str(self.created)

class DepositedItems(models.Model):
    seller_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="deposit_skin_user")
    seller_trade_link = models.CharField(max_length=128)
    seller_api_key = models.CharField(max_length=128, default='')
    asset_id = models.CharField(max_length=128)
    item_name = models.CharField(max_length=128)
    item_wear = models.CharField(max_length=128)
    item_skinline_name = models.CharField(max_length=128, default='')
    item_d_para = models.CharField(max_length=128)
    market_hash_name = models.CharField(max_length=128)
    offer_price = models.DecimalField(max_digits=32, decimal_places=2)
    icon_url = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    offer_state = models.CharField(max_length=128)
    buyer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="withdraw_skin_user", null=True)
    buyer_trade_link = models.CharField(max_length=128)
    buyer_api_key = models.CharField(max_length=128, default='')
    buyer_item_count = models.IntegerField(default=0)

    def get_time_diff(self):
        if self.updated:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            timediff = now - self.updated
            return timediff.total_seconds()