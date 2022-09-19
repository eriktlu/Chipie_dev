import asyncio
from audioop import mul
import json
import random
from hashlib import pbkdf2_hmac
from decimal import Decimal

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from django.utils.crypto import get_random_string

from .models import Messages, CustomUser, Roulette, RouletteBets

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_group_name = 'chat'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message room web socket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        name = data['name']
        username = data['username']

        await self.save_message(name, message, username)

        avatar = await self.get_user_avater(name)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'name': name,
                'username': username,
                'avatar': avatar,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        name = event['name']
        username = event['username']
        avatar = event['avatar']

        await self.send(text_data=json.dumps({
            'message': message,
            'name': name,
            'username': username,
            'avatar': avatar,
        }))

    def get_object(self, name):
        return CustomUser.objects.get(name=name)

    @sync_to_async
    def save_message(self, name, message, username):
        if not message:
            return
        else:
            user_obj = self.get_object(name)
            Messages.objects.create(name=user_obj, content=message, username=username)

    @sync_to_async
    def get_user_avater(self, name):
        if not name:
            return
        else:
            user_obj = self.get_object(name)
            return user_obj.avatar


# ROULETTE


@database_sync_to_async
def get_round():
    a = Roulette.objects.last()
    if a:
        return a.round_number
    else:
        return 1
    

# @database_sync_to_async
# def save_roll(self, result, roll_color, round_number):
#     winners = RouletteBets.objects.filter(round_number=round_number, bet_choice=roll_color)
#     multiplier = 0

#     if roll_color == 'blue' or roll_color == 'red':
#         multiplier = 2
#     elif roll_color == 'green':
#         multiplier = 14

#     for winner in winners:
#         winner_id = winner.steamid
#         winner_bet = winner.bet_value

#         userObj = CustomUser.objects.filter(steam_id=winner_id)[0]
#         newBalance = userObj.user_coins + (winner_bet * multiplier)
#         CustomUser.objects.filter(steam_id=winner_id).update(user_coins=newBalance)

#     print('test rulett')
#     Roulette.objects.create(win = result, roll_color = roll_color, round_number = round_number, is_over = True)

# @database_sync_to_async
# def get_previous_results():
#     prev_results = Roulette.objects.all().order_by('-id')[:10]
#     prev_results_list = []
#     for result in prev_results:
#         prev_results_list.append(result.roll_color)

#     return prev_results_list



@database_sync_to_async
def save_bet(steamid, betValue, betChoice, round, steamname):
    userObj = CustomUser.objects.filter(steam_id=steamid)[0]
    rouletteObj = Roulette.objects.filter(round_number=round)[0]

    if Decimal(str(userObj.user_coins)) < Decimal(str(betValue)):
        return False

    newBalance = float(str(userObj.user_coins)) - float(str(betValue))

    CustomUser.objects.filter(steam_id=steamid).update(user_coins=newBalance)
    
    RouletteBets.objects.create(user=userObj, bet_value=betValue, bet_choice=betChoice, round=rouletteObj, win_amount=-abs(Decimal(betValue)))

    return True

@database_sync_to_async
def get_balance(steamid):
    userObj = CustomUser.objects.filter(steam_id=steamid)[0]
    return userObj.user_coins

@database_sync_to_async
def get_bets(round):
    rouletteObj = Roulette.objects.filter(round_number=round)[0]
    rouletteBetsObj = RouletteBets.objects.filter(round=rouletteObj)

    bets = {}

    for idx, bet in enumerate(rouletteBetsObj):
        bets[str(idx)] = {}
        bets[str(idx)].update({
            'username': bet.user.username,
            'bet_color': bet.bet_choice,
            'bet_value': str(bet.bet_value)
        })

    return bets

class RouletteGame(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = 'roulette'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # while self.connected:
        #     await asyncio.sleep(5)
  
            

    async def receive(self, text_data):
        pass

    async def roulette_game(self, event):
        result = event['data']['round_result']
        prev_results = event['data']['prev_results']
        rount_start = event['data']['round_start']

        print(event)

        await self.send(text_data = json.dumps({
            'type': 'test',
            'round_result': result,
            'previous_results': prev_results,
            'round_start': rount_start
        }))

    async def disconnect(self, close_code):
        #Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

class RouletteBet(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_group_name = 'roulette_bet'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        steamid = data['steamid']
        betValue = data['betValue']
        betChoice = data['bet_choice']
        steamName = data['steamname']
        avatar = data['avatar']

        round = await get_round()

        if betChoice == 'red' or betChoice == 'green' or betChoice == 'blue':
            betSaved = await save_bet(steamid, betValue, betChoice, round, steamName)

            if betSaved is True:

                balance = await get_balance(steamid)
                bets = await get_bets(round)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_bet',
                        'steamname': steamName,
                        'betcolor': betChoice,
                        'bets': bets,
                        'betValue': betValue,
                        'avatar': avatar,
                    }
                )

                await self.send(text_data = json.dumps({
                    'balance': json.dumps(balance, cls=DecimalEncoder),
                }))

            else:
                print("Not enough Balance!")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_bet_error'
                    }
                )


    async def send_bet(self, event):
        steamname = event['steamname']
        betcolor = event['betcolor']
        bets = event['bets']
        betvalue = event['betValue']
        avatar = event['avatar']

        await self.send(text_data=json.dumps({
            'steamname': steamname,
            'betcolor': betcolor,
            'bets': bets,
            'betvalue': betvalue,
            'avatar': avatar,
        }))

    async def send_bet_error(self, event):

        await self.send(text_data=json.dumps({
            'error': 'There was a problem adding your bet!'
        }))

    async def disconnect(self, close_code):
        pass

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)














class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_group_name = self.scope['user'].steam_id
        except:
             self.room_group_name = '0'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification',
                'message': message
            }
        )

    async def notification(self, event):
        message = event['message']

        print('got in here')

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 1
        }))

    async def notification_error(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 2
        }))

    async def buyer_notifications(self, event):
        message = event['message']
        seller_tradelink = event['seller_tradelink']
        asset_id = event['asset_id']
        seller_id = event['seller_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'seller_tradelink': seller_tradelink,
            'asset_id': asset_id,
            'seller_id': seller_id,
            'buyer_notifications': True
        }))

    async def seller_notifications(self, event):
        message = event['message']
        asset_id = event['asset_id']
        buyer_id = event['buyer_id']
        item_image = event['item_image']
        item_name = event['item_name']
        item_skinline_name = event['item_skinline_name']
        item_condition = event['item_condition']

        await self.send(text_data=json.dumps({
            'message': message,
            'asset_id': asset_id,
            'buyer_id': buyer_id,
            'item_image': item_image,
            'item_name': item_name,
            'item_skinline_name': item_skinline_name,
            'item_condition': item_condition,
            'seller_notifications': True
        }))

    # Receive message from WebSocket
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']

    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': message
    #         }
    #     )

    # # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']

    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))