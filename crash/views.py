from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from main.models import CustomUser, Messages
from .models import Crash, CrashBets


@login_required
def crash(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    crashObj = Crash.objects.latest('round_start_time')
    lastBetsObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]
    
    prev_results = Crash.objects.filter(over=True).order_by('-id')[:10]
    prev_results_list = []
    for result in prev_results:
        prev_results_list.append(str(result.result))

    if lastBetsObj.timer < 20 and lastBetsObj.timer > 15:
        betsObj = CrashBets.objects.filter(crash_round=crashObj.round_number-1)
        betsTotalValue = CrashBets.objects.filter(crash_round=crashObj.round_number-1).aggregate(Sum('bet_value'))
        totalBets = CrashBets.objects.filter(crash_round=crashObj.round_number-1).count()
    else:
        betsObj = CrashBets.objects.filter(crash_round=crashObj)
        betsTotalValue = CrashBets.objects.filter(crash_round=crashObj).aggregate(Sum('bet_value'))
        totalBets = CrashBets.objects.filter(crash_round=crashObj).count()


    context = {
        'coins': userObj.user_coins,
        'bets': betsObj,
        'prev_results': prev_results_list,
        'chatMessages': messages,
        'bets_total_value': betsTotalValue['bet_value__sum'],
        'total_bets': totalBets,
    }
    return render(request, 'crash/crash.html', context)