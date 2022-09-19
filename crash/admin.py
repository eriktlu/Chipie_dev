from django.contrib import admin

from .models import *

class CrashAdmin(admin.ModelAdmin):
    list_display = ['id', 'result', 'round_number', 'used_server_seed', 'used_public_seed', 'round_start_time']

class CrashBetsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'crash_round', 'bet_value', 'win', 'created']


admin.site.register(Crash, CrashAdmin)
admin.site.register(CrashBets, CrashBetsAdmin)
admin.site.register(CrashServerSeeds)
admin.site.register(CrashPublicSeeds)
