from audioop import mul
from tracemalloc import stop
from schedule import Scheduler
import threading
import time
import requests
import channels.layers
import random
import asyncio
import json
import hmac
import math
import decimal

import hashlib

from time import sleep

from hashlib import sha256

from decimal import *

import datetime
from hashlib import pbkdf2_hmac

from apscheduler.schedulers.background  import BackgroundScheduler
from django.utils.crypto import get_random_string

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

from steampy.utils import GameOptions
from steampy.client import SteamClient

from django.db.models import Q
from .models import CustomUser, TradeOffers, CsgoItems, Roulette, RouletteBets, RouletteServerSeeds, RoulettePublicSeeds
from crash.models import CrashServerSeeds, CrashPublicSeeds, Crash, CrashBets
from casebattle.models import CaseBattleServerSeed
from deposit.models import DepositedItems

import apscheduler.schedulers.background

scheduler = apscheduler.schedulers.background.BackgroundScheduler({'apscheduler.job_defaults.max_instances': 2})

getcontext().prec = 2

# @database_sync_to_async
def get_round():
    a = Roulette.objects.last()
    if a:
        return a.round_number
    else:
        return 1
    

def get_this_game_result(round):
    rouletteObj = Roulette.objects.filter(round_number=round)[0]

    return rouletteObj.win

# @database_sync_to_async
def save_roll(result, roll_color, round_number, server_seed, public_seed):
    publicSeedObj = RoulettePublicSeeds.objects.filter(public_seed=public_seed)[0]
    serverSeedObj = RouletteServerSeeds.objects.filter(server_seed=server_seed)[0]

    Roulette.objects.create(win = result, roll_color = roll_color, round_number = round_number, is_over = True, used_server_seed=serverSeedObj, used_public_seed=publicSeedObj)

    rouletteObj = Roulette.objects.filter(round_number=round_number-1)[0]
    winners = RouletteBets.objects.filter(round=rouletteObj, bet_choice=rouletteObj.roll_color)
    multiplier = 0

    print(rouletteObj.roll_color)
    print(roll_color)

    if rouletteObj.roll_color == 'blue' or rouletteObj.roll_color == 'red':
        multiplier = 2
    elif rouletteObj.roll_color == 'green':
        multiplier = 14

    for winner in winners:

        print(winner.user.username)
        winner_id = winner.user.steam_id
        winner_bet = winner.bet_value

        userObj = CustomUser.objects.filter(steam_id=winner_id)[0]
        newBalance = float(str(userObj.user_coins)) + float(float(str(winner_bet)) * float(str(multiplier)))
        CustomUser.objects.filter(steam_id=winner_id).update(user_coins=newBalance)
        RouletteBets.objects.filter(id=winner.id).update(win=True, win_amount=float(str(winner_bet))*float(str(multiplier)))

# @database_sync_to_async
def get_previous_results():
    prev_results = Roulette.objects.all().order_by('-id')[:10]
    prev_results_list = []
    for result in prev_results:
        prev_results_list.append(result.roll_color)

    return prev_results_list

# @database_sync_to_async
def get_previous_crash_results():
    prev_results = Crash.objects.all().order_by('-id')[:10]
    prev_results_list = []
    for result in prev_results:
        prev_results_list.append(str(result.result))

    return prev_results_list

def calc_roulette():
    rouletteStartTime = datetime.datetime.now().time()
    rouletteStartTime = json.dumps(rouletteStartTime, indent=4, sort_keys=True, default=str)

    server_seed = RouletteServerSeeds.objects.latest('date_added')
    public_seed = RoulettePublicSeeds.objects.latest('date_added')
    round = get_round() + 1

    hash = hmac.new(bytes(str(server_seed), 'utf-8'), bytes(str(public_seed) + '-' + str(round), 'utf-8'), hashlib.sha256)

    result = int(hash.hexdigest()[0:8], 16) % 15

    roll_color = ''

    if result == 0:
        roll_color = 'green'
    elif result >= 1 and result <= 7:
        roll_color = 'blue'
    elif result >= 8 and result <= 14:
        roll_color = 'red'

    prev_results = get_previous_results()
    live_result = get_this_game_result(round-1)
    save_roll(result, roll_color, round, server_seed, public_seed)
    

    # group_name = '76561198027134295'
    # channel_layer = channels.layers.get_channel_layer()

    # async_to_sync(channel_layer.group_send)(
    #     group_name,
    #     {
    #         'type': 'notification',
    #         'message': 'Test message for notifications'
    #     }
    # )

    data = {
        'prev_results': prev_results,
        'round_result': live_result,
        'round_start': rouletteStartTime
    }

    run_roulette(data)

def run_roulette(data, **kwargs):
    group_name = 'roulette'
    channel_layer = channels.layers.get_channel_layer()

    async_to_sync(channel_layer.group_send)(
                group_name,
            {
                'type': 'roulette_game',
                'data': data
            }
        )


def check_trades():
    items_to_check = DepositedItems.objects.filter(offer_state='Withdraw accepted')

    for item in items_to_check:

        if item.get_time_diff() > 1200:
            user = CustomUser.objects.filter(steam_id=item.buyer_id.steam_id)[0]
            new_coins = user.user_coins + item.offer_price
            CustomUser.objects.filter(steam_id=item.buyer_id.steam_id).update(user_coins=new_coins)
            DepositedItems.objects.filter(id=item.id).update(offer_state="Trade Failed due time limit")
        else:
            print(item.seller_id.steam_id)
            response = requests.get('https://steamcommunity.com/inventory/%s/%s/%s' % (item.seller_id.steam_id, 730, 2) )
            inventorySeller = response.json()

            sellerInvList = []
            for sellerItem in inventorySeller['assets']:
                sellerInvList.append(sellerItem['assetid'])

            if item.asset_id in sellerInvList:
                print('Item still in the invetnory')
            else:
                print('Item not in seller inventory')

                response = requests.get('https://steamcommunity.com/inventory/%s/%s/%s' % (item.buyer_id, 730, 2) )
                inventoryBuyer = response.json()

                print(item.buyer_id)

                desc = {bItem['classid']: 
                [
                    bItem['name'],
                    bItem['market_hash_name'],
                    bItem['icon_url'],
                    bItem['tradable'],
                    bItem['actions'] if 'actions' in bItem else None
                ] for bItem in inventoryBuyer['descriptions']}

                items = [[bitem['assetid'], desc[bitem['classid']]] for bitem in inventoryBuyer['assets']]

                buyerItemCount = 0
                for buyerItem in items:
                    if buyerItem[1][1] == item.market_hash_name:
                        buyerItemCount = buyerItemCount + 1
                
                if buyerItemCount > item.buyer_item_count:
                    print("Item transferred to buyer")
                    user = CustomUser.objects.filter(steam_id=item.seller_id.steam_id)[0]
                    new_coins = user.user_coins + item.offer_price
                    CustomUser.objects.filter(steam_id=item.seller_id.steam_id).update(user_coins=new_coins)
                    DepositedItems.objects.filter(id=item.id).update(offer_state="Trade Complete")
                else:
                    print("Item not transfered to buyer")
                    user = CustomUser.objects.filter(steam_id=item.buyer_id.steam_id)[0]
                    new_coins = user.user_coins + item.offer_price
                    CustomUser.objects.filter(steam_id=item.buyer_id.steam_id).update(user_coins=new_coins)
                    DepositedItems.objects.filter(id=item.id).update(offer_state="Trade Failed")

def runCrash():
    crashServerSeedObj = CrashServerSeeds.objects.latest('date_added')
    crashPublicSeedObj = CrashPublicSeeds.objects.latest('date_added')
    crashPreviousRoundObj = Crash.objects.latest('round_start_time').round_number

    INSTANT_CRASH_P = 6.66

    h = hmac.new(bytes(crashServerSeedObj.server_seed, 'utf-8'), bytes(crashPublicSeedObj.public_seed + '-' + str(crashPreviousRoundObj+1), 'utf-8'), hashlib.sha256)         
    x = int(h.hexdigest()[0:13], 16)
    z = math.pow(2, 52)

    result = (100 * z - x) / (z - x)
    house = 1 - (INSTANT_CRASH_P / 100)
    endResult = max(100, result * house) / 100

    newGame = Crash(result=endResult, round_number=crashPreviousRoundObj+1, over=False, used_server_seed=crashServerSeedObj, used_public_seed=crashPublicSeedObj)
    newGame.save()

    # print(result * house)
    # print(endResult)

def crashOver():
    crashObj = Crash.objects.latest('round_start_time')

    crashOver = crashObj.over

    print(crashOver)

    if crashOver == True:
        runCrash()

def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run

Scheduler.run_continuously = run_continuously

def updateSeeds():
    roulette_server_seed = get_random_string(length=64)

    hash = hashlib.sha256(roulette_server_seed.encode('utf-8'))
    hashed_crash_server_seed = hash.hexdigest()

    rouletteS = RouletteServerSeeds(server_seed=roulette_server_seed, hashed_server_seed=hashed_crash_server_seed)
    rouletteS.save()

    roulette_public_seed = get_random_string(length=32)

    rouletteP = RoulettePublicSeeds(public_seed=roulette_public_seed)
    rouletteP.save()



    crash_server_seed = get_random_string(length=64)

    hash = hashlib.sha256(crash_server_seed.encode('utf-8'))
    hashed_crash_server_seed = hash.hexdigest()

    crashS = CrashServerSeeds(server_seed=crash_server_seed, hashed_server_seed=hashed_crash_server_seed)
    crashS.save()


    crash_public_seed = get_random_string(length=32)

    crashP = CrashPublicSeeds(public_seed=crash_public_seed)
    crashP.save()


    casebattle_server_seed = get_random_string(length=64)

    hash = hashlib.sha256(casebattle_server_seed.encode('utf-8'))
    hashed_casebattle_server_seed = hash.hexdigest()

    casebattleS = CaseBattleServerSeed(server_seed=casebattle_server_seed, hashed_server_seed=hashed_casebattle_server_seed)
    casebattleS.save()

def crashBets():
    crashObj = Crash.objects.latest('round_start_time')
    crashBetObj = CrashBets.objects.filter(crash_round=crashObj, win=None)

    for bet in crashBetObj:
        if bet.stop_point <= crashObj.result and bet.stop_point != 0:
            win_amount = float(str(bet.bet_value)) * float(str(bet.stop_point))
            newBalance = float(str(bet.user.user_coins)) + float(str(win_amount))
            CrashBets.objects.filter(id=bet.id).update(win=True, total_result=Decimal(win_amount))
            CustomUser.objects.filter(steam_id=str(bet.user.steam_id)).update(user_coins=newBalance)
        else:
            CrashBets.objects.filter(id=bet.id).update(win=False)



def crash_game():
    crashObj = Crash.objects.latest('round_start_time')
    lastCrashObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]

    group_name = 'crash'
    channel_layer = channels.layers.get_channel_layer()

    if lastCrashObj.timer > 0:
        # run timer
        oldTimer = lastCrashObj.timer
        newTimer = Decimal(str(oldTimer)) - Decimal('.1')

        # bets = get_bets(False, None, newTimer)

        Crash.objects.filter(round_number=crashObj.round_number-1).update(timer=newTimer)
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'testtimer',
                'timer': str(newTimer),
                'result': str(lastCrashObj.result),
                'game': 2,
                # 'bets': bets
            }
        )

        if newTimer == 0:
            pass

    else:
        if crashObj.over == False:
            # run game
            if crashObj.result == Decimal(str('1')):
                newState = Decimal(str('1'))
            else:
                oldState = crashObj.result_state
                adder = math.floor(Decimal(str(oldState)) / Decimal(str('1'))) / 100
                newState = Decimal(str(oldState)) + decimal.Decimal(str(adder))

            # bets = get_bets(True, newState, None)

            Crash.objects.filter(id=crashObj.id).update(result_state=newState)

            if newState >= crashObj.result:
                Crash.objects.filter(id=crashObj.id).update(over=True)
                prev_results = get_previous_crash_results()
                crashBets()
                crashOver()
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'testtry',
                        'state': str(crashObj.result),
                        'game': 1,
                        # 'bets': bets,
                        'prev_results': prev_results
                    }
                )
                return

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'testtry',
                    'state': str(newState),
                    'game': 0,
                    # 'bets': bets
                }
            )

def get_bets(current, state, timer):
    crashObj = Crash.objects.latest('round_start_time')
    if current is True:
        crashBetsObj = CrashBets.objects.filter(crash_round=crashObj)

        cBets = {}

        for idx, bet in enumerate(crashBetsObj):
            stopPoint = 0
            if bet.stop_point != 0 and bet.stop_point < state:
                stopPoint = 'Won'
            else:
                if bet.stop_point == 0:
                    stopPoint = 'Live'
                else:
                    stopPoint = bet.stop_point

            cBets[str(idx)] = {}
            cBets[str(idx)].update({
                'username': bet.user.username,
                'bet_value': str(bet.bet_value),
                'stop_point': str(stopPoint),
                'r_stop': str(bet.stop_point),
                'steamid': bet.user.steam_id,
            })
        return cBets
    else:
        cBets = {}

        if timer > 15:
            lastCrashObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]
            crashBetsObj = CrashBets.objects.filter(crash_round=lastCrashObj)
            for idx, bet in enumerate(crashBetsObj):
                win = 'Crashed'
                if bet.win is True:
                    win = 'Won'

                cBets[str(idx)] = {}
                cBets[str(idx)].update({
                    'username': bet.user.username,
                    'bet_value': str(bet.bet_value),
                    'stop_point': win,
                    'r_stop': str(bet.stop_point),
                    'steamid': bet.user.steam_id,
                })
            return cBets
        
        else:
            crashBetsObj = CrashBets.objects.filter(crash_round=crashObj)
            for idx, bet in enumerate(crashBetsObj):
                stop_point = bet.stop_point
                if bet.stop_point == 0:
                    stop_point = 'Live'

                cBets[str(idx)] = {}
                cBets[str(idx)].update({
                    'username': bet.user.username,
                    'steamid': bet.user.steam_id,
                    'bet_value': str(bet.bet_value),
                    'stop_point': str(stop_point),
                    'r_stop': str(bet.stop_point),
                    'timer': True
                })
            return cBets
            

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def tick():
    print(datetime.datetime.now().time())

def start():
    scheduler = Scheduler()

    apscheduler = BackgroundScheduler()
    apscheduler.add_job(calc_roulette, 'interval', seconds=30)
    apscheduler.add_job(check_trades, 'interval', seconds=10)
    apscheduler.add_job(updateSeeds, 'interval', hours=1)
    apscheduler.add_job(crash_game, 'interval', seconds=0.1)
    apscheduler.start()
    scheduler.run_continuously()