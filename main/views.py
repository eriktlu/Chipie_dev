from http import client
from django.shortcuts import render, redirect

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from main.storehouse import sendTradeWithdrawSessionControl, sendTradeDepositeSessionControl

from django.db.models import Q
from .models import Messages, CustomUser, CsgoItems, TradeOffers, Roulette, RouletteBets
from crash.models import CrashBets, Crash
from deposit.models import DepositedItems, Deposit
from casebattle.models import CaseBattle, CaseBattleRoom

from django.core.paginator import Paginator

from itertools import chain

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import CustomUserSerializer, MessagesSerializer

from django.http import JsonResponse

import requests

from asgiref.sync import async_to_sync
import channels.layers

from json import dumps


from steampy.client import SteamClient
from steampy.utils import GameOptions

APP_ID = 730
CONTEXT_ID = 2

# Create your views here.

# Logs user out of their account
def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    if request.user.is_authenticated and not request.user.is_superuser:        
        username = request.GET.get('username', 'Anonymous')
        messages = Messages.objects.filter().order_by('-id')[0:25]

        social = request.user.social_auth.get(provider='steam')
        uid = social.extra_data['player']['steamid']

        userObj = CustomUser.objects.filter(steam_id=str(uid))[0]


        prev_results = Roulette.objects.all().order_by('-id')[1:11]
        prev_results_list = []
        for result in prev_results:
            prev_results_list.append(result.roll_color)

        roulette_data = Roulette.objects.last()
        latest_bets = RouletteBets.objects.filter(round=roulette_data)
        latest_bets_arr = []
        latest_bets_total_arr = [0, 0, 0, 0, 0 ,0]
        blue_total = 0
        blue_total_v = 0
        red_total = 0
        red_total_v = 0
        green_total = 0
        green_total_v = 0

        rouletteLastRoll = Roulette.objects.get(round_number=roulette_data.round_number)
        lastRollTime = rouletteLastRoll.get_time_diff()
        # print(lastRollTime)

        for bets in latest_bets:
            latest_bets_arr.append([bets.user.username, bets.bet_choice, str(bets.bet_value), bets.user.avatar])
            if bets.bet_choice == 'blue':
                blue_total += 1
                blue_total_v += bets.bet_value
            elif bets.bet_choice == 'red':
                red_total += 1
                red_total_v += bets.bet_value
            elif bets.bet_choice == 'green':
                green_total += 1
                green_total_v += bets.bet_value
            latest_bets_total_arr = [str(blue_total), str(blue_total_v), str(red_total), str(red_total_v), str(green_total), str(green_total_v)]

        print(latest_bets_total_arr)
        response = requests.get('https://steamcommunity.com/inventory/%s/%s/%s' % (uid, APP_ID, CONTEXT_ID) )
        inventory = response.json()

        user = request.user

        context = {
            'inventory': inventory,
            'chatMessages': messages,
            'username': username,
            'user': user,
            'coins': userObj.user_coins,
            'prev_roulette_rolls': prev_results_list,
            'latest_bets': latest_bets_arr,
            'latest_bets_total_arr': latest_bets_total_arr,
            'timeDiff': lastRollTime
        }

        return render(request, 'main/home.html', context)
    

    prev_results = Roulette.objects.all().order_by('-id')[1:11]
    prev_results_list = []
    for result in prev_results:
        prev_results_list.append(result.roll_color)

    roulette_data = Roulette.objects.last()
    latest_bets = RouletteBets.objects.filter(round=roulette_data)
    latest_bets_arr = []
    latest_bets_total_arr = [0, 0, 0, 0, 0 ,0]
    blue_total = 0
    blue_total_v = 0
    red_total = 0
    red_total_v = 0
    green_total = 0
    green_total_v = 0

    rouletteLastRoll = Roulette.objects.get(round_number=roulette_data.round_number)
    lastRollTime = rouletteLastRoll.get_time_diff()
    # print(lastRollTime)

    for bets in latest_bets:
        latest_bets_arr.append([bets.user.username, bets.bet_choice, str(bets.bet_value), bets.user.avatar])
        if bets.bet_choice == 'blue':
            blue_total += 1
            blue_total_v += bets.bet_value
        elif bets.bet_choice == 'red':
            red_total += 1
            red_total_v += bets.bet_value
        elif bets.bet_choice == 'green':
            green_total += 1
            green_total_v += bets.bet_value
        latest_bets_total_arr = [str(blue_total), str(blue_total_v), str(red_total), str(red_total_v), str(green_total), str(green_total_v)]


    context = {
        'prev_roulette_rolls': prev_results_list,
        'latest_bets': latest_bets_arr,
        'latest_bets_total_arr': latest_bets_total_arr,
        'timeDiff': lastRollTime
    }

    return render(request, 'main/home.html', context)

@login_required(login_url='/login/steam/')
def profile(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    depositedItems = DepositedItems.objects.filter(seller_id=userObj, offer_state='Withdraw accepted')

    roulette_bets = RouletteBets.objects.filter(user=userObj).order_by('-id')
    crash_bets = CrashBets.objects.filter(user=userObj).order_by('-id')
    cb_bets = CaseBattle.objects.filter(user=userObj).order_by('-id')

    wall = list(chain(roulette_bets, crash_bets, cb_bets))
    wall.sort(key=lambda x: x.created, reverse=True)
    game_transactions = []
    # print(wall)
    for item in wall:
        # game_transactions[str(idx)] = {}
        try:
            game_transactions.append({
                'round_number': item.room.round_number,
                'result': item.total_result,
                'game': item.game,
                'date': item.created
            })
            # print(item.room.round_number)
            # print(item.battle_result_coins)
            # print(item.game)
            # print(item.created)
        except:
            pass

        try:
            game_transactions.append({
                'round_number': item.round.round_number,
                'result': item.win_amount,
                'game': item.game,
                'date': item.created
            })
            # print(item.round.round_number)
            # print(item.win_amount)
            # print(item.game)
            # print(item.created)
        except:
            pass

        try:
            game_transactions.append({
                'round_number': item.crash_round.round_number,
                'result': item.total_result,
                'game': item.game,
                'date': item.created
            })
            # print(item.crash_round.round_number)
            # print(item.bet_value)
            # print(item.game)
            # print(item.created)
        except:
            pass

    paginator = Paginator(game_transactions, 10)
    page_number = request.GET.get('page')
    x = False
    
    page_obj = paginator.get_page(page_number)

    transactions = Deposit.objects.filter(steam_id=userObj)
    transactions_p = Paginator(transactions, 10)
    t_page_number = request.GET.get('transaction')

    t_page_obj = transactions_p.get_page(t_page_number)


    if page_number is not None or t_page_number is not None:
        x = True

    # if TradeOffers.objects.filter(name__name=uid).exists():
    #     tradeOffers = TradeOffers.objects.filter(name__name=uid)

    #     context = {
    #         'coins': userObj.user_coins,
    #         'trade_offers': tradeOffers
    #     }
    #     return render(request, 'main/profile.html', context)

    if request.method == 'POST':
        newClientSeed = request.POST.get('user_client_seed')
        newTradeLink = request.POST.get('user_trade_link')

        # CaseBattleClientSeed.objects.filter(user=userObj).update(client_seed=newClientSeed)
        CustomUser.objects.filter(steam_id=str(uid)).update(trade_link=newTradeLink, client_seed=newClientSeed)

        # clientSeedObj = CaseBattleClientSeed.objects.filter(user=userObj)[0]

        userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

        # context = {
        #     'coins': userObj.user_coins,
        #     'chatMessages': messages,
        #     'depositedItems': depositedItems,
        #     'client_seed': clientSeedObj.client_seed,
        # }
        # return render(request, 'main/profile.html', context)

    clientSeed = userObj.client_seed
    userTradeLink = userObj.trade_link

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
        'depositedItems': depositedItems,
        'client_seed': clientSeed,
        'roulette_bets': roulette_bets,
        'crash_bets': crash_bets,
        'cb_bets': cb_bets,
        'trade_link': userTradeLink,
        'transactions': transactions_p,
        'game_transactions': paginator,
        'page_obj': page_obj,
        't_page_obj': t_page_obj,
        'x': x
    }
    return render(request, 'main/profile.html', context)




# Selle bloki saad copida uue lehe tegemisel, muuta vaja aint funktsiooni nime ja html faili nime.
@login_required
def privacyPolicy(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'main/privacypolicy.html', context)

@login_required
def fairness(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    rouletteObj = Roulette.objects.all().order_by('-used_server_seed', '-round_start_time').distinct('used_server_seed')

    roulettePaginator = Paginator(rouletteObj, 10)
    roulette_page_number = request.GET.get('roulette')
    
    roulette_page_obj = roulettePaginator.get_page(roulette_page_number)


    crashObj = Crash.objects.all().order_by('-used_server_seed', '-round_start_time').distinct('used_server_seed')

    crashPaginator = Paginator(crashObj, 10)
    crash_page_number = request.GET.get('crash')
    x = 0

    if crash_page_number:
        x = 1
    
    crash_page_obj = crashPaginator.get_page(crash_page_number)


    caseBattleObj = CaseBattleRoom.objects.filter(battle_state='Game started').order_by('-used_server_seed', '-room_created').distinct('used_server_seed')

    caseBattlePaginator = Paginator(caseBattleObj, 10)
    caseBattle_page_number = request.GET.get('caseBattle')

    if caseBattle_page_number:
        x = 2
    
    caseBattle_page_obj = caseBattlePaginator.get_page(caseBattle_page_number)

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
        'roulettes': roulette_page_obj,
        'crashes': crash_page_obj,
        'casebattles': caseBattle_page_obj,
        'x': x,

    }
    return render(request, 'main/fairness.html', context)

def get_coins(request):
    try:
        social = request.user.social_auth.get(provider='steam')
        uid = social.extra_data['player']['steamid']

        userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

        return JsonResponse({'coins': userObj.user_coins})
    except:
        return JsonResponse({'coins': 0})
