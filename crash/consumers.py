import hmac
import hashlib
import json

import channels.layers

from asgiref.sync import async_to_sync

from decimal import Decimal

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from main.models import CustomUser
from .models import *


class CrashConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'crash'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'testtry',
                'test': text_data_json['a']
            }
        )
        
        
    async def testtry(self, event):
        state = event['state']
        game = event['game']
        # bets = event['bets']

        try:
            prev_results = event['prev_results']

            await self.send(text_data=json.dumps({
                'state': state,
                'game': game,
                # 'bets': bets,
                'prev_results': prev_results
            }))
        
        except:
            await self.send(text_data=json.dumps({
                'state': state,
                'game': game,
                # 'bets': bets
            }))
        

    async def testtimer(self, event):
        timer = event['timer']
        game = event['game']
        result = event['result']
        # bets = event['bets']

        await self.send(text_data=json.dumps({
            'timer': timer,
            'game': game,
            'result': result,
            # 'bets': bets
        }))

class CrashBetConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'crash_bet'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        try:
            text_data_json['cash_out']
            bet_win = await check_bet(text_data_json['user_id'])
            username = await get_username(text_data_json['user_id'])
            steam_id = await get_steamid(text_data_json['user_id'])

            if bet_win is True:
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'crash_bet_won',
                        'username': username,
                        'steam_id': steam_id,
                    }
                )
            else:
                pass
        except:
            bet_value = Decimal(text_data_json['bet_value'])
            decimal_points = bet_value.as_tuple().exponent

            username = await get_username(text_data_json['user_id'])
            steam_id = await get_steamid(text_data_json['user_id'])
            avatar = await get_avatar(text_data_json['user_id'])

            if decimal_points >= -2:

                try:
                    fixedValue = text_data_json['fixed_value']

                    if Decimal(fixedValue) > Decimal(str(1)):
                    
                        bet = await register_fixed_bet(text_data_json['user_id'], bet_value, fixedValue)
                        crashBets = await get_bets()

                        if bet is True:
                            await self.channel_layer.group_send(
                                self.room_group_name,
                                {
                                    'type': 'add_fixed_crash_bet',
                                    'bet_value': text_data_json['bet_value'],
                                    'username': username,
                                    'fixed_value': fixedValue,
                                    'crash_bets': crashBets,
                                    'avatar': avatar,
                                    'steam_id': steam_id,
                                }
                            )
                        else:
                            group_name = str(steam_id)
                            channel_layer = channels.layers.get_channel_layer()

                            await channel_layer.group_send(
                                group_name,
                                {
                                    'type': 'notification_error',
                                    'message': 'Bet Failed!'
                                }
                            )

                    else:
                        group_name = str(steam_id)
                        channel_layer = channels.layers.get_channel_layer()

                        await channel_layer.group_send(
                            group_name,
                            {
                                'type': 'notification_error',
                                'message': 'Bet Failed!'
                            }
                        )

                except:
                    bet = await register_bet(text_data_json['user_id'], bet_value)
                    crashBets = await get_bets()
                    
                    if bet is True:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'add_crash_bet',
                                'bet_value': text_data_json['bet_value'],
                                'username': username,
                                'crash_bets': crashBets,
                                'avatar': avatar,
                                'steam_id': steam_id,
                            }
                        )
                    else:
                       

                        group_name = str(steam_id)
                        channel_layer = channels.layers.get_channel_layer()

                        print(group_name)

                        await channel_layer.group_send(
                            group_name,
                            {
                                'type': 'notification_error',
                                'message': 'Bet Failed!'
                            }
                        )

    async def add_crash_bet(self, event):
        bet_value = event['bet_value']
        username = event['username']
        crash_bets = event['crash_bets']
        avatar = event['avatar']
        steam_id = event['steam_id']

        await self.send(text_data=json.dumps({
            'bet_value': bet_value,
            'username': username,
            'crash_bets': crash_bets,
            'avatar': avatar,
            'steam_id': steam_id,
        }))

    async def add_fixed_crash_bet(self, event):
        bet_value = event['bet_value']
        username = event['username']
        fixed_value = event['fixed_value']
        crash_bets = event['crash_bets']
        avatar = event['avatar']
        steam_id = event['steam_id']

        await self.send(text_data=json.dumps({
            'bet_value': bet_value,
            'username': username,
            'fixed_value': fixed_value,
            'crash_bets': crash_bets,
            'avatar': avatar,
            'steam_id': steam_id,
        }))

    async def crash_bet_won(self, event):
        username = event['username']
        steamid = event['steam_id']

        await self.send(text_data=json.dumps({
            'won_username': username,
            'won_steamid': steamid,
        }))


@database_sync_to_async
def register_bet(steamid, value):
    crashObj = Crash.objects.latest('round_start_time')
    lastCrashObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]

    if lastCrashObj.timer < Decimal(20) and lastCrashObj.timer > Decimal(0):
        userObj = CustomUser.objects.filter(steam_id=str(steamid))[0]

        try:
            userObj = CrashBets.objects.filter(user=userObj, win=None)[0]

            return False
        except:

            if userObj.user_coins >= Decimal(value):
                newBalance = float(str(userObj.user_coins)) - float(str(value))
                CustomUser.objects.filter(steam_id=str(steamid)).update(user_coins=newBalance)

                crashBet = CrashBets(user=userObj, crash_round=crashObj, bet_value=Decimal(value), bet_choice='Live', total_result=-abs(Decimal(value)))
                crashBet.save()

                return True
            else:
                print('Not enough coins')
                return False
    else:
        print('Not a time to bet')
        return False

@database_sync_to_async
def register_fixed_bet(steamid, value, fixedValue):
    crashObj = Crash.objects.latest('round_start_time')
    lastCrashObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]

    if lastCrashObj.timer < Decimal(20) and lastCrashObj.timer > Decimal(0):
        userObj = CustomUser.objects.filter(steam_id=str(steamid))[0]

        # try:
        #     userObj = CrashBets.objects.filter(user=userObj, win=None)[0]

        #     return False
        # except:

        if userObj.user_coins >= Decimal(value):
            newBalance = float(str(userObj.user_coins)) - float(str(value))
            CustomUser.objects.filter(steam_id=str(steamid)).update(user_coins=newBalance)

            crashBet = CrashBets(user=userObj, crash_round=crashObj, bet_value=Decimal(value), stop_point=Decimal(fixedValue), bet_choice='Fixed', total_result=-abs(Decimal(value)))
            crashBet.save()

            return True
        else:
            print('Not enough coins')
            return False
    else:
        print('Not a time to bet')
        return False

@database_sync_to_async
def get_username(steamid):
    username = CustomUser.objects.filter(steam_id=str(steamid))[0].username

    return username

@database_sync_to_async
def get_steamid(steamid):
    steamid = CustomUser.objects.filter(steam_id=str(steamid))[0].steam_id

    return steamid

@database_sync_to_async
def get_avatar(steamid):
    avatar = CustomUser.objects.filter(steam_id=str(steamid))[0].avatar

    return avatar

@database_sync_to_async
def check_bet(steamid):
    userObj = CustomUser.objects.filter(steam_id=str(steamid))[0]
    crashObj = Crash.objects.latest('round_start_time')
    try:
        crashBetObj = CrashBets.objects.filter(user=userObj, win=None, stop_point=0)[0]
        if crashObj.result_state <= crashObj.result:
            win_amount = float(str(crashBetObj.bet_value)) * float(str(crashObj.result_state))
            newBalance = float(str(userObj.user_coins)) + float(str(win_amount))
            CrashBets.objects.filter(id=crashBetObj.id).update(win=True, stop_point=crashObj.result_state, total_result=Decimal(win_amount))
            CustomUser.objects.filter(steam_id=str(steamid)).update(user_coins=newBalance)
            
            return True
        else:
            CrashBets.objects.filter(id=crashBetObj.id).update(win=False, stop_point=crashObj.result_state)
    except:
        return False

@database_sync_to_async
def get_bets():
    crashObj = Crash.objects.latest('round_start_time')
    crashBetsObj = CrashBets.objects.filter(crash_round=crashObj)

    cBets = {}

    for idx, bet in enumerate(crashBetsObj):
        cBets[str(idx)] = {}
        cBets[str(idx)].update({
            'username': bet.user.username,
            'bet_value': str(bet.bet_value),
            # 'stop_point': bet.stop_point
        })
    return cBets
