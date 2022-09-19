import requests
import json
import logging

import math

import re

from django.contrib import messages as send_notification

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from test_cs import settings

from main.models import CustomUser, CsgoItems, Messages
from main.storehouse import sendTradeWithdrawSessionControl, sendTradeDepositeSessionControl

from paypalcheckoutsdk.orders import OrdersGetRequest
from .paypal import PayPalClient

from coinbase_commerce.client import Client
from coinbase_commerce.error import SignatureVerificationError, WebhookInvalidPayload
from coinbase_commerce.webhook import Webhook

from .models import Deposit, DepositedItems
from decimal import Decimal

from .ptpSkins import DepositItem


APP_ID = 730
CONTEXT_ID = 2

@login_required
def depositOptions(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'deposit/deposit.html', context)

@login_required
def depositSkins(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    if userObj.trade_link in [None, '']:
        send_notification.error(request, 'You need to set trade link before accessing deposit page!')

        return redirect("profile")
    else:
        print('inside')

    response = requests.get('https://steamcommunity.com/inventory/%s/%s/%s' % (uid, APP_ID, CONTEXT_ID) )
    inventory = response.json()

    if inventory is not None:
        print(inventory)

        desc = {item['classid']: 
        [
            item['name'].split('|')[0],
            item['market_hash_name'],
            item['icon_url'],
            item['tradable'],
            item['actions'] if 'actions' in item else None,
            item['name'].split('|')[1] if item['tradable'] is 1 else None,
            re.search(r'\((.*?)\)',item['market_hash_name']).group(1) if item['tradable'] is 1 else None
        ] for item in inventory['descriptions']}

        items = [[item['assetid'], desc[item['classid']]] for item in inventory['assets']]

    else:
        items = None

    # print(inventory['descriptions'][1]['actions'][0]['link'])
    # print(items)

    if request.method == 'POST':
        item_id = request.POST.get('item_name')
        trade_url = userObj.trade_link
        item_price = request.POST.get('deposit-item-value')
        # api_key = request.POST.get('api_key')

        item_name = ''
        item_hash_name = ''
        item_icon = ''
        item_inspect_link = ''

        for item in items:
            if item[0] == item_id:
                print(item)
                item_name = item[1][0]
                item_hash_name = item[1][1]
                item_icon = item[1][2]
                item_inspect_link = item[1][4][0]['link']
                item_skinline_name = item[1][5]
                item_condition = item[1][6]

        
        item_inspect_id = item_inspect_link.split("%D")
        depositItem = DepositItem(userObj, item_id, item_inspect_id[1], trade_url, item_price, item_name, item_hash_name, item_icon, item_skinline_name, item_condition)

        if depositItem is True:
            send_notification.success(request, 'Item successfully deposited!')
        else:
            send_notification.error(request, 'There was a problem depositing your item!')

        return redirect("deposit:deposit-skins")
        # profile_url = social.extra_data['player']['profileurl']
        # profile_url_split = profile_url.split('/')
        # steam_name = profile_url_split[4]


    try:
        trade_item = DepositedItems.objects.filter(offer_state = 'Withdraw accepted')[0]
        timeDiff = 20 - math.floor(trade_item.get_time_diff() / 60)
        trade_on = ''
        trade_off = 'display-none'

        context = {
            'coins': userObj.user_coins,
            'inventory': items,
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
            'inventory': items,
            'chatMessages': messages,
            'trade_on': trade_on,
            'trade_off': trade_off
        }

    return render(request, 'deposit/depositSkins.html', context)

@login_required
def depositPayPal(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }

    return render(request, 'deposit/depositPayPal.html', context)

@login_required
def paymentComplete(request):
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body['orderID']

    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']

    user_ins = CustomUser.objects.get(steam_id=uid)

    requestOrder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestOrder)

    total_paid = response.result.purchase_units[0].amount.value

    gold_gain = Decimal(total_paid) * 9

    Deposit.objects.create(
        steam_id = user_ins,
        transaction_value_money = Decimal(total_paid),
        transaction_value_gold = gold_gain,
        country_code = response.result.purchase_units[0].shipping.address.country_code,
        payment_option = "paypal",
        billing_status=True,
    )

    userObj = CustomUser.objects.filter(steam_id=uid)[0]
    newBalance = Decimal(str(userObj.user_coins)) + Decimal(str(gold_gain))
    CustomUser.objects.filter(steam_id=uid).update(user_coins=newBalance)

    return JsonResponse("Payment completed!", safe=False)

@login_required
def paymentSuccessful(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'deposit/depositSuccess.html', context)

@login_required
def paymentCancel(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }
    return render(request, 'deposit/depositCancel.html', context)

@login_required
def cryptoPayment(request):
    social = request.user.social_auth.get(provider='steam')
    uid = social.extra_data['player']['steamid']
    country_code = social.extra_data['player']['loccountrycode']
    messages = Messages.objects.filter().order_by('-id')[0:25]

    userObj = CustomUser.objects.filter(steam_id=str(uid))[0]

    if request.method == 'POST':
        deposit_amount = request.POST.get('deposit_amount_money')

        client = Client(api_key=settings.COINBASE_COMMERCE_API_KEY)
        domain_url = 'https://testcsgocircus.herokuapp.com/'
        # domain_url = 'http://localhost:8000/'
        product = {
            'name': 'Deposit',
            'description': 'Deposit on the website',
            'local_price': {
                'amount': deposit_amount,
                'currency': 'EUR'
            },
            'metadata': {
                'customer_id': uid if uid else None,
                'country_code': country_code if country_code else None,
            },
            'pricing_type': 'fixed_price',
            'redirect_url': domain_url + 'deposit/successful/',
            'cancel_url': domain_url + 'deposit/cancelled/',
        }
        charge = client.charge.create(**product)

        # return render(request, 'deposit/depositCrypto.html', {
        #     'charge': charge,
        #     'coins': userObj.user_coins,
        #     'chatMessages': messages,
        # })
    
        return redirect(charge.hosted_url)

    context = {
        'coins': userObj.user_coins,
        'chatMessages': messages,
    }

    return render(request, 'deposit/depositCrypto.html', context)

@csrf_exempt
@require_http_methods(['POST'])
def coinbase_webhook(request):
    print("Entered webhook")
    logger = logging.getLogger(__name__)

    request_data = request.body.decode('utf-8')
    request_sig = request.headers.get('X-CC-Webhook-Signature', None)
    webhook_secret = settings.COINBASE_COMMERCE_WEBHOOK_SHARED_SECRET

    try:
        event = Webhook.construct_event(request_data, request_sig, webhook_secret)

        # List of all Coinbase webhook events:
        # https://commerce.coinbase.com/docs/api/#webhooks

        if event['type'] == 'charge:confirmed':
            print('Entered confirmed webhook')
            logger.info('Payment confirmed.')

            steam_id = event['data']['metadata']['customer_id']
            userObj = CustomUser.objects.filter(steam_id=str(steam_id))[0]
            country_code = event['data']['metadata']['country_code']

            total_paid = event['data']['local']['amount']
            print(event['data']['local']['amount'])
            print(event['data']['local']['currency'])

            gold_gain = Decimal(total_paid) * 9

            userObj = CustomUser.objects.filter(steam_id=steam_id)[0]
            newBalance = Decimal(str(userObj.user_coins)) + Decimal(str(gold_gain))
            CustomUser.objects.filter(steam_id=steam_id).update(user_coins=newBalance)

            print(gold_gain)

            Deposit.objects.create(
                steam_id = userObj,
                transaction_value_money = Decimal(total_paid),
                transaction_value_gold = gold_gain,
                country_code = country_code,
                payment_option = "paypal",
                billing_status=True,
            )

    except (SignatureVerificationError, WebhookInvalidPayload) as e:
        return HttpResponse(e, status=400)

    logger.info(f'Received event: id={event.id}, type={event.type}')
    return HttpResponse('ok', status=200)