from django.contrib import admin

from .models import *

class CaseBattleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room', 'room_seat', 'battle_result', 'battle_result_coins', 'roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'used_client_seed', 'total_result']

class CaseBattleRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_creator', 'package', 'room_name', 'round_number', 'battle_state', 'battle_result_value', 'winner_count', 'used_server_seed']

class CaseBattlePackagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'chest']

class CaseBattleChestsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'value']

class CaseBattleChestItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'chest', 'item_name', 'item_value', 'item_odds']

admin.site.register(CaseBattle, CaseBattleAdmin)
admin.site.register(CaseBattleRoom, CaseBattleRoomAdmin)
admin.site.register(CaseBattlePackages, CaseBattlePackagesAdmin)
# admin.site.register(CaseBattleClientSeed)
admin.site.register(CaseBattleServerSeed)
admin.site.register(CaseBattleChests, CaseBattleChestsAdmin)
admin.site.register(CaseBattleChestItems, CaseBattleChestItemsAdmin)
