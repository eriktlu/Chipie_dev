from django.contrib import admin

from .models import *

class DepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'steam_id', 'transaction_value_money', 'transaction_value_gold', 'country_code', 'payment_option', 'billing_status']

class DepositItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller_id', 'seller_trade_link', 'seller_api_key', 'asset_id', 'item_name', 'market_hash_name', 'item_wear', 'offer_price', 'icon_url', 'offer_state', 'buyer_id', 'buyer_api_key']

admin.site.register(Deposit, DepositAdmin)
admin.site.register(DepositedItems, DepositItemsAdmin)