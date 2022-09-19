from deposit.models import DepositedItems
from main.models import CustomUser

from django.utils import timezone

from asgiref.sync import async_to_sync
import channels.layers
import requests
from decimal import Decimal

def skinOfferAccepted(id, trade_link, userObj, api_key=None):
    try:
        DepositedItems.objects.filter(buyer_id=userObj, offer_state='Withdraw accepted')[0]

        return "Failed"
    except:
    
        chosenItem = DepositedItems.objects.get(id=int(id))

        if(userObj.user_coins > chosenItem.offer_price):
            response = requests.get('https://steamcommunity.com/inventory/%s/%s/%s' % (userObj.steam_id, 730, 2) )
            inventorySeller = response.json()

            depositedItem = DepositedItems.objects.filter(id=id)[0]

            item_count = 0

            for item in inventorySeller['descriptions']:
                if item['market_hash_name'] == depositedItem.market_hash_name:
                    item_count = item_count + 1


            new_coins = Decimal(str(userObj.user_coins)) - Decimal(str(chosenItem.offer_price))
            CustomUser.objects.filter(steam_id=userObj.steam_id).update(user_coins=new_coins)
            DepositedItems.objects.filter(id=id).update(buyer_id=userObj, buyer_trade_link=trade_link, offer_state='Withdraw accepted', updated=timezone.now())
            
            # group_name = steam_id
            # channel_layer = channels.layers.get_channel_layer()

            # async_to_sync(channel_layer.group_send)(
            #     group_name,
            #     {
            #         'type': 'buyer_notifications',
            #         'seller_tradelink': depositedItem.seller_trade_link,
            #         'asset_id': depositedItem.asset_id,
            #         'seller_id': depositedItem.seller_id.steam_id,
            #         'message': 'You have 20 minutes to finish the trade'
            #     }
            # )

            group_name = depositedItem.seller_id.steam_id
            channel_layer = channels.layers.get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'seller_notifications',
                    'asset_id': depositedItem.asset_id,
                    'buyer_id': userObj.steam_id,
                    'item_image': depositedItem.icon_url,
                    'item_name': depositedItem.item_name,
                    'item_skinline_name': depositedItem.item_skinline_name,
                    'item_condition': depositedItem.item_wear,
                    'message': 'BUYER FOUND'
                }
            )

            return "Succeeded"
        else:
            return "Failed"