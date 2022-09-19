from django.contrib import admin

# Register your models here.

from .models import *

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'steam_id', 'name']

class CsgoItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'market_hash_name', 'item_value']

class RouletteAdmin(admin.ModelAdmin):
    list_display = ['id', 'win', 'roll_color', 'round_number', 'round_start_time', 'is_over']

class RouletteBetsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'round', 'bet_value', 'bet_choice']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Messages)
admin.site.register(TradeOffers)
admin.site.register(CsgoItems, CsgoItemsAdmin)
admin.site.register(Roulette, RouletteAdmin)
admin.site.register(RouletteBets, RouletteBetsAdmin)
admin.site.register(RoulettePublicSeeds)
admin.site.register(RouletteServerSeeds)