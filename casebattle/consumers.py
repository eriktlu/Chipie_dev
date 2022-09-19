import json
import hmac
import hashlib

from django.core.serializers.json import DjangoJSONEncoder

from decimal import Decimal

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import CaseBattle, CaseBattlePackages, CaseBattleRoom, CaseBattleServerSeed, CaseBattleChests, CaseBattleChestItems
from main.models import CustomUser

from django.db.models import Max

class CaseBattleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'cb_%s' % self.room_name

        

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
        print(text_data_json)

        game = await add_player(text_data_json['user_id'], text_data_json['room_name'], text_data_json['seat'])
        userObj = await get_avatar(text_data_json['user_id'])

        if game is True:
            skin_data = await get_skin_data(text_data_json['room_name'])
            game_results = await start_game(text_data_json['room_name'])
            players_results = await results_to_list(game_results)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'casebattle_game',
                    'room_name': text_data_json['room_name'],
                    'seat': text_data_json['seat'],
                    'avatar': userObj.avatar,
                    'username': userObj.username,
                    'results': players_results,
                    'skin_data': skin_data,
                }
            )

        if game is False:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'casebattle_seat',
                    'seat': text_data_json['seat'],
                    'avatar': userObj.avatar,
                    'username': userObj.username,
                }
            )
        pass

    async def casebattle_game(self, event):
        seat = event['seat']
        avatar = event['avatar']
        username = event['username']
        players_results = event['results']
        skin_data = event['skin_data']

        await self.send(text_data=json.dumps({
            'results': players_results,
            'seat': seat,
            'avatar': avatar,
            'username': username,
            'skin_data': skin_data,
        }))

    async def casebattle_seat(self, event):
        seat = event['seat']
        avatar = event['avatar']
        username = event['username']

        await self.send(text_data=json.dumps({
            'seat': seat,
            'avatar': avatar,
            'username': username,
        }))


@database_sync_to_async
def get_avatar(steamid):
    userObj = CustomUser.objects.filter(steam_id=str(steamid))[0]

    return userObj

@database_sync_to_async
def add_player(steamid, room_name, seat):
    userObj = CustomUser.objects.filter(steam_id=str(steamid))[0]
    roomObj = CaseBattleRoom.objects.filter(room_name=room_name, battle_state='Room active')[0]

    playersInRoom = CaseBattle.objects.filter(room=roomObj)

    count = 0
    for player in playersInRoom:
        count = count + 1

    print("Count: ", count)
    if count >= 4:
        print("Maximum players already reached")
        return
    elif count > 0 and count < 4:
        playersInSeat = CaseBattle.objects.filter(room=roomObj, room_seat=seat)
        for player in playersInSeat:
            print("There's a player in that seat already")
            return

        multipleAccountCheck = CaseBattle.objects.filter(user=userObj, room=roomObj)
        for player in multipleAccountCheck:
            print("Player is already in room")
            return

        if Decimal(str(userObj.user_coins)) >= Decimal(str(roomObj.package.price)):

            newBalance = float(str(userObj.user_coins)) - float(str(roomObj.package.price))
            CustomUser.objects.filter(steam_id=steamid).update(user_coins=newBalance)

            CaseBattle.objects.create(user=userObj, room=roomObj, room_seat=seat, total_result=-abs(roomObj.package.price))
            print("Player added to the room")

            if count == 3:
                return True
            else:
                return False
        
        else:
            print("Not enough Balance!")
            return

@database_sync_to_async
def start_game(room_name):
    roomObj = CaseBattleRoom.objects.filter(room_name=room_name, battle_state='Room active')[0]
    serverSeedObj = CaseBattleServerSeed.objects.latest('seed_generated_date')
    CaseBattleRoom.objects.filter(room_name=room_name, battle_state='Room active').update(battle_state='Game started', used_server_seed=serverSeedObj)

    players = CaseBattle.objects.filter(room=roomObj)

    round_number = roomObj.round_number
    total_winnings = Decimal(0)

    itemsObj = CaseBattleChestItems.objects.filter(chest=roomObj.package.chest)
    itemDict = {}

    for idx, item in enumerate(itemsObj):
        itemDict[idx + 1] = {}
        itemDict[idx + 1].update({'name': item.item_name, 'value': item.item_value, 'odds': item.item_odds})

    for player in players:        
        clientSeed = player.user.client_seed

        roll_number = 1
        coinValue = 0

        for _ in range(5):
            print("Started Loop")
            h = hmac.new(bytes(serverSeedObj.server_seed, 'utf-8'), bytes(clientSeed + '-' + str(round_number) + '-' + str(roll_number) + '-'  + str(player.room_seat), 'utf-8'), hashlib.sha256)
            
            result = int(h.hexdigest()[0:5], 16)

            if result > 999999:
                result = int(h.hexdigest()[5:10], 16)
                if result > 999999:
                    result = int(h.hexdigest()[10:15], 16)
                    if result > 999999:
                        result = int(h.hexdigest()[15:20], 16)
                        if result > 999999:
                            result = int(h.hexdigest()[20:25], 16)
                            if result > 999999:
                                result = int(h.hexdigest()[25:30], 16)
                                if result > 999999:
                                    result = int(h.hexdigest()[30:35], 16)
                                    if result > 999999:
                                        result = int(h.hexdigest()[35:40], 16)
                                        if result > 999999:
                                            result = int(h.hexdigest()[40:45], 16)
                                            if result > 999999:
                                                result = int(h.hexdigest()[45:50], 16)
                                                if result > 999999:
                                                    result = int(h.hexdigest()[50:55], 16)
                                                    if result > 999999:
                                                        result = int(h.hexdigest()[55:60], 16)

            result = result%(10000) + 1

            fieldName = 'roll_' + str(_ + 1)
            
            startN = 0
            rolledItem = 0

            print("Result: ", result)
            
            for item in itemDict:
                endN = startN + itemDict[item]['odds'] * 10000
                print("Start number: ", str(startN))
                print("End number: ", str(endN))

                if result > startN and result <= endN:
                    rolledItem = item
                    CaseBattle.objects.filter(user=player.user, room=roomObj).update(**{fieldName: CaseBattleChestItems.objects.filter(chest=roomObj.package.chest, item_name=itemDict[item]['name'])[0]})
                    
                    coinValue = coinValue + itemDict[item]['value']
                    total_winnings = total_winnings + itemDict[item]['value']
                    break
                else:
                    startN = endN

            print('WINNER: ', rolledItem)
            roll_number = roll_number + 1
        
        CaseBattle.objects.filter(user=player.user, room=roomObj).update(used_client_seed=clientSeed, battle_result_coins=coinValue, battle_result='Lose')

    highestCoinValue = players.aggregate(Max('battle_result_coins'))
    winners = CaseBattle.objects.filter(room=roomObj, battle_result_coins=highestCoinValue['battle_result_coins__max'])
    winner_count = 0

    for winner in winners:
        CaseBattle.objects.filter(user=winner.user, room=roomObj).update(battle_result='Win')
        winner_count = winner_count + 1

    CaseBattleRoom.objects.filter(room_name=room_name, room_creator=roomObj.room_creator).update(battle_result_value=total_winnings, winner_count=winner_count)

    total_winnings = total_winnings / winner_count

    for winner in winners:
        newBalance = Decimal(str(winner.user.user_coins)) + Decimal(str(total_winnings))
        CustomUser.objects.filter(steam_id=winner.user.steam_id).update(user_coins=newBalance)
        CaseBattle.objects.filter(user=winner.user, room=roomObj).update(total_result=Decimal(total_winnings))

    print("Total Winnings: ", total_winnings)
    print("Divided between: ", winner_count)

    latest = CaseBattle.objects.filter(room=roomObj)

    return latest


@database_sync_to_async
def results_to_list(results):
    playersResults = {'total_value': str(results[0].room.battle_result_value), 'winner_count': results[0].room.winner_count}

    for idx, player in enumerate(results):
        playersResults[str(player.room_seat)] = {}
        playersResults[str(player.room_seat)].update({
            'rolls_names': [player.roll_1.item_name, player.roll_2.item_name, player.roll_3.item_name, player.roll_4.item_name, player.roll_5.item_name],
            'roll_exterior': [player.roll_1.exterior_name, player.roll_2.exterior_name, player.roll_3.exterior_name, player.roll_4.exterior_name, player.roll_5.exterior_name],
            'roll_color': [player.roll_1.skinline_color, player.roll_2.skinline_color, player.roll_3.skinline_color, player.roll_4.skinline_color, player.roll_5.skinline_color],
            'roll_skinline': [player.roll_1.skinline_name, player.roll_2.skinline_name, player.roll_3.skinline_name, player.roll_4.skinline_name, player.roll_5.skinline_name],
            'roll_image': [player.roll_1.url, player.roll_2.url, player.roll_3.url, player.roll_4.url, player.roll_5.url],
            'rolls_values': [str(player.roll_1.item_value), str(player.roll_2.item_value), str(player.roll_3.item_value), str(player.roll_4.item_value), str(player.roll_5.item_value)],
            'battle_result': player.battle_result, 
            'battle_result_coins': str(player.battle_result_coins),
        }) 
    return playersResults


@database_sync_to_async
def get_skin_data(roomName):
    roomObj = CaseBattleRoom.objects.filter(room_name=roomName, battle_state='Room active')[0]
    itemsObj = CaseBattleChestItems.objects.filter(chest=roomObj.package.chest)

    skinData = {}

    for item in itemsObj:
        skinData[item.item_name] = {}
        skinData[item.item_name].update({
            'item_name': item.item_name,
            'item_value': str(item.item_value),
            'item_image_url': item.url,
            'item_exterior': item.exterior_name,
            'item_skinline': item.skinline_name,
            'item_color': item.skinline_color,
            'item_odds': str(item.item_odds)
        })

    return skinData

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)