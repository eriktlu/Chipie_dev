from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
import math

from django.contrib import messages as send_notification

from steampy.client import SteamClient

import requests

from test_cs import settings

from main.models import CustomUser, CsgoItems, Messages
from deposit.models import DepositedItems
# from .models import Withdraw

from .crypto import BtcWithdraw
from .bitcash import BtchWithdraw
from .ptpSkinsWithdraw import skinOfferAccepted


@login_required
def withdrawOptions(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'withdraw/withdraw.html', context)

@login_required
def withdrawBtc(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    if request.method == 'POST':
        coins_to_withdraw = request.POST.get('withdraw_coins_amount')
        wallet_address = request.POST.get('user_btc_wallet_address')

        print(coins_to_withdraw)
        print(wallet_address)

        country_code = social.extra_data['player']['loccountrycode']
        user_ins = CustomUser.objects.get(steam_id=uid)

        trans_id = BtcWithdraw(wallet_address, coins_to_withdraw, user_ins, country_code)
        BtchWithdraw(wallet_address, coins_to_withdraw, user_ins, country_code)
        context = {
            'coins': userObj.user_coins,
            'ctw': coins_to_withdraw,
            'wa': wallet_address,
            'trans_id': trans_id,
            'chatMessages': messages,
        }
        
        return render(request, 'withdraw/withdrawBtc.html', context)

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'withdraw/withdrawBtc.html', context)


#SKINS
@login_required(login_url='/login/steam/')
def withdrawCSGOskins(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]
    messages = Messages.objects.filter().order_by('-id')[0:25]

    if userObj.trade_link in [None, '']:
        send_notification.error(request, 'You need to set trade link before accessing withdraw page!')

        return redirect("profile")
    else:
        print('inside')

    five_minutes_ago = timezone.now() + datetime.timedelta(minutes=-15)
    DepositedItems.objects.filter(offer_state='Listed', created__lt=five_minutes_ago).update(offer_state='Expired')
    inventory = DepositedItems.objects.filter(offer_state='Listed', created__gte=five_minutes_ago)

    # response = requests.get("http://steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198027134295A24963854190D12252612783761308457")
    # test = response.json()

    # print(test)
    
    # steam_client = SteamClient('9729383EE7551AD9FF429F638E14EEFE')
    # params = {'key': '9729383EE7551AD9FF429F638E14EEFE'}
    # client = SteamClient('9729383EE7551AD9FF429F638E14EEFE')
    # offers = client.get_trade_offers()
    # summaries =  steam_client.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1', params).json()


    if request.method == 'POST':
        if 'filter-option' in request.POST:
            filterOption = request.POST.get('filter-option')

            if filterOption is 'low':
                inventory = DepositedItems.objects.filter(offer_state='Listed', created__gte=five_minutes_ago).order_by('-created')
            elif filterOption is 'high':
                inventory = DepositedItems.objects.filter(offer_state='Listed', created__gte=five_minutes_ago).order_by('-offer_price')
            else:
                inventory = DepositedItems.objects.filter(offer_state='Listed', created__gte=five_minutes_ago).order_by('offer_price')


        else:

            id = request.POST.get('item_name')
            trade_url = userObj.trade_link
            api_key = request.POST.get('api_key')

            offerMsg = skinOfferAccepted(id, trade_url, userObj, api_key)

            # Getting trade link
            # profile_url = social.extra_data['player']['profileurl']
            # profile_url_split = profile_url.split('/')
            # steam_name = profile_url_split[4]

            userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

            return redirect("withdraw:withdraw-skins")

    try:
        trade_item = DepositedItems.objects.filter(buyer_id=userObj, offer_state = 'Withdraw accepted')[0]
        timeDiff = 20 - math.floor(trade_item.get_time_diff() / 60)
        trade_on = ''
        trade_off = 'display-none'

        context = {
            'coins': userObj.user_coins,
            'inventory': inventory,
            'chatMessages': messages,
            'trade_on': trade_on,
            'trade_off': trade_off,
            'trade_item': trade_item,
            'time_diff': timeDiff,
        }

    except:
        trade_on = 'display-none'
        trade_off = ''


        context = {
            'coins': userObj.user_coins,
            'inventory': inventory,
            'chatMessages': messages,
            'trade_on': trade_on,
            'trade_off': trade_off
        }

    return render(request, 'withdraw/withdrawSkins.html', context)