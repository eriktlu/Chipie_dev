from re import A
from attr import asdict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from main.models import CustomUser, Messages
from .models import CaseBattle, CaseBattleRoom, CaseBattlePackages, CaseBattleChests, CaseBattleChestItems
from django.db.models import Max

from django.utils.crypto import get_random_string

from decimal import Decimal

from django.contrib import messages as send_notification

# Create your views here.
@login_required
def caseBattle(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    caseBattleRooms = CaseBattleRoom.objects.filter(battle_state='Room active')

    caseBattle = CaseBattle.objects.filter(room__battle_state='Room active')

    rooms = {}

    for cb in caseBattle:
        if cb.room.room_name not in rooms:
            rooms[cb.room.room_name] = {
                'price': cb.room.package.price,
                'package_img': cb.room.package.avatar,
                'users': []
            }    

        rooms[cb.room.room_name]['users'].append(cb.user.avatar)

    packages = CaseBattlePackages.objects.filter()

    # if request.method == 'POST':
    #     deleteRoom = request.POST.get('delete_room')

    #     if deleteRoom != '':
    #         CaseBattleRoom.objects.filter(room_name=deleteRoom).update(battle_state='Room deactivated')


    if request.method == 'POST':
        if request.POST.get('delete'):
            roomName = request.POST.get('delete')
            instance = CaseBattleRoom.objects.filter(room_name=roomName, battle_state='Room active')

            print(instance.count())

            if instance.count() > 0:
                newBalance = Decimal(str(userObj.user_coins)) + Decimal(str(instance[0].package.price))
                CustomUser.objects.filter(steam_id=userObj.steam_id).update(user_coins=newBalance)

                userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

                instance.update(battle_state='Deleted')

                caseBattle = CaseBattle.objects.filter(room__battle_state='Room active')

                rooms = {}

                for cb in caseBattle:
                    if cb.room.room_name not in rooms:
                        rooms[cb.room.room_name] = {
                            'price': cb.room.package.price,
                            'package_img': cb.room.package.avatar,
                            'users': []
                        }    

                    rooms[cb.room.room_name]['users'].append(cb.user.avatar)

                send_notification.success(request, 'Room Deleted!')

                context = {
                    'coins': userObj.user_coins,
                    'rooms': caseBattleRooms,
                    'packages': packages,
                    'chatMessages': messages,
                    'x': rooms,
                }
                return render(request, 'casebattle/casebattle.html', context)
            else:
                context = {
                    'coins': userObj.user_coins,
                    'rooms': caseBattleRooms,
                    'packages': packages,
                    'chatMessages': messages,
                    'x': rooms,
                    'error': 'There was a problem with deleting your room!'
                }
                return render(request, 'casebattle/casebattle.html', context)

            

        room_name = get_random_string(length=10)

        cbPackage = request.POST.get('cb_package')

        if cbPackage:
            if int(cbPackage) > 0:
                chosenPackage = CaseBattlePackages.objects.filter(id=cbPackage)[0]
                if userObj.user_coins >= chosenPackage.price:
                    round = get_round() + 1

                    newBalance = float(str(userObj.user_coins)) - float(str(chosenPackage.price))
                    CustomUser.objects.filter(steam_id=uid).update(user_coins=newBalance)

                    CaseBattleRoom.objects.create(room_creator=userObj, package=chosenPackage, room_name=room_name, round_number=round, battle_state='Room active')

                    roomObj = CaseBattleRoom.objects.filter(room_name=room_name)[0]

                    CaseBattle.objects.create(user=userObj, room=roomObj, room_seat=1, total_result=-abs(chosenPackage.price))

                    response = redirect('/casebattle/rooms/%s/' % room_name)
                    return response
                else:
                    context = {
                        'coins': userObj.user_coins,
                        'rooms': caseBattleRooms,
                        'packages': packages,
                        'chatMessages': messages,
                        'error': 'Not enough coins'
                    }
                    return render(request, 'casebattle/casebattle.html', context)
    

    context = {
        'coins': userObj.user_coins,
        'rooms': caseBattleRooms,
        'chatMessages': messages,
        'packages': packages,
        'x': rooms,
    }
    return render(request, 'casebattle/casebattle.html', context)

@login_required
def createBattle(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    packages = CaseBattlePackages.objects.filter()



    if request.method == 'POST':
        room_name = get_random_string(length=10)

        cbPackage = request.POST.get('cb_package')

        if cbPackage.isnumeric() is True:
            if int(cbPackage) > 0:
                chosenPackage = CaseBattlePackages.objects.filter(id=cbPackage)[0]
                if userObj.user_coins >= chosenPackage.price:
                    round = get_round() + 1

                    newBalance = float(str(userObj.user_coins)) - float(str(chosenPackage.price))
                    CustomUser.objects.filter(steam_id=uid).update(user_coins=newBalance)

                    CaseBattleRoom.objects.create(room_creator=userObj, package=chosenPackage, room_name=room_name, round_number=round, battle_state='Room active')

                    roomObj = CaseBattleRoom.objects.filter(room_name=room_name)[0]

                    CaseBattle.objects.create(user=userObj, room=roomObj, room_seat=1)

                    response = redirect('/casebattle/rooms/%s/' % room_name)
                    return response
                else:
                    context = {
                        'coins': userObj.user_coins,
                        'packages': packages,
                        'chatMessages': messages,
                        'error': 'Not enough coins'
                    }
                    return render(request, 'casebattle/createBattle.html', context) 

    context = {
        'coins': userObj.user_coins,
        'packages': packages,
        'chatMessages': messages,
    }
    return render(request, 'casebattle/createBattle.html', context)

@login_required
def battleRoom(request, room_name):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    cbRoom = CaseBattleRoom.objects.filter(room_name=room_name)[0]
    cbChestItemsObj = CaseBattleChestItems.objects.filter(chest=cbRoom.package.chest)

    cbObj = CaseBattle.objects.filter(room=cbRoom)
    cbArr = []
    cbDict = {'game_started': False}
    for cb in cbObj:
        if cb.room_seat == 1:
            cbArr.append(1)
        if cb.room_seat == 2:
            cbArr.append(2)
        if cb.room_seat == 3:
            cbArr.append(3)
        if cb.room_seat == 4:
            cbArr.append(4)

        cbDict[cb.room_seat] = {}
        cbDict[cb.room_seat].update({
            'player_icon': cb.user.avatar,
            'player_name': cb.user.username,
        })

        if cbRoom.battle_state == "Game started":
            cbDict[cb.room_seat]['items'] = {}

            cbDict[cb.room_seat]['items'][1] = {}
            cbDict[cb.room_seat]['items'][1].update({
                'item_names': cb.roll_1.item_name,
                'item_values': cb.roll_1.item_value,
                'item_url': cb.roll_1.url,
                'item_skinline': cb.roll_1.skinline_name,
                'item_color': cb.roll_1.skinline_color,
                'item_exterior': cb.roll_1.exterior_name,
            })

            cbDict[cb.room_seat]['items'][2] = {}
            cbDict[cb.room_seat]['items'][2].update({
                'item_names': cb.roll_2.item_name,
                'item_values': cb.roll_2.item_value,
                'item_url': cb.roll_2.url,
                'item_skinline': cb.roll_2.skinline_name,
                'item_color': cb.roll_2.skinline_color,
                'item_exterior': cb.roll_2.exterior_name,
            })

            cbDict[cb.room_seat]['items'][3] = {}
            cbDict[cb.room_seat]['items'][3].update({
                'item_names': cb.roll_3.item_name,
                'item_values': cb.roll_3.item_value,
                'item_url': cb.roll_3.url,
                'item_skinline': cb.roll_3.skinline_name,
                'item_color': cb.roll_3.skinline_color,
                'item_exterior': cb.roll_3.exterior_name,
            })

            cbDict[cb.room_seat]['items'][4] = {}
            cbDict[cb.room_seat]['items'][4].update({
                'item_names': cb.roll_4.item_name,
                'item_values': cb.roll_4.item_value,
                'item_url': cb.roll_4.url,
                'item_skinline': cb.roll_4.skinline_name,
                'item_color': cb.roll_4.skinline_color,
                'item_exterior': cb.roll_4.exterior_name,
            })

            cbDict[cb.room_seat]['items'][5] = {}
            cbDict[cb.room_seat]['items'][5].update({
                'item_names': cb.roll_5.item_name,
                'item_values': cb.roll_5.item_value,
                'item_url': cb.roll_5.url,
                'item_skinline': cb.roll_5.skinline_name,
                'item_color': cb.roll_5.skinline_color,
                'item_exterior': cb.roll_5.exterior_name,
            })
            
            
            
            
            
            cbDict[cb.room_seat].update({
                # 'item_names': [cb.roll_1.item_name, cb.roll_2.item_name, cb.roll_3.item_name, cb.roll_4.item_name, cb.roll_5.item_name],
                # 'item_values': [cb.roll_1.item_value, cb.roll_2.item_value, cb.roll_3.item_value, cb.roll_4.item_value, cb.roll_5.item_value],
                # 'item_url': [cb.roll_1.url, cb.roll_2.url, cb.roll_3.url, cb.roll_4.url, cb.roll_5.url],
                # 'item_skinline': [cb.roll_1.skinline_name, cb.roll_2.skinline_name, cb.roll_3.skinline_name, cb.roll_4.skinline_name, cb.roll_5.skinline_name],
                # 'item_color': [cb.roll_1.skinline_color, cb.roll_2.skinline_color, cb.roll_3.skinline_color, cb.roll_4.skinline_color, cb.roll_5.skinline_color],
                # 'item_exterior': [cb.roll_1.exterior_name, cb.roll_2.exterior_name, cb.roll_3.exterior_name, cb.roll_4.exterior_name, cb.roll_5.exterior_name],
                'battle_result': cb.battle_result,
                'battle_result_coins': cb.battle_result_coins,
            })
        else:
            cbDict[cb.room_seat].update({
                'battle_result_coins': '0.00',
            })
    if cbRoom.battle_state == "Game started":
        cbDict.update({
            'total_value': cbRoom.battle_result_value,
            'winner_count': cbRoom.winner_count,
            'game_started': True,
        })

    context = {
        'coins': userObj.user_coins,
        'room_name': room_name,
        'test': cbRoom.package.chest,
        'items': cbChestItemsObj,
        'cb': cbArr,
        'room_creator': cbRoom.room_creator,
        'playersData': cbDict,
        'chatMessages': messages,
        'package_price': cbRoom.package.price,
    }
    return render(request, 'casebattle/battleRoom.html', context)



def get_round():
    caseBattleRoundObj = CaseBattleRoom.objects.last()
    if caseBattleRoundObj:
        return caseBattleRoundObj.round_number
    else:
        return 0