from .models import DepositedItems

from django.db.models import Q



def DepositItem(user_id, item_id, item_inspect_id, trade_url, item_price, item_name, item_hash_name, item_icon, item_skinline_name, item_condition, steam_api=None ):
    print(steam_api)


    try:
        existing_item = DepositedItems.objects.filter(Q(asset_id=item_id, offer_state='Listed') | Q(asset_id=item_id, offer_state='Withdraw accepted') )[0]

        print('Item already listed')
        return False
    except:
        DepositedItems.objects.create(
            seller_id = user_id,
            seller_trade_link = trade_url,
            # seller_api_key = steam_api,
            asset_id = item_id,
            item_d_para = item_inspect_id,
            item_name = item_name,
            item_wear = item_condition,
            item_skinline_name = item_skinline_name, 
            market_hash_name=item_hash_name,
            offer_price=item_price,
            icon_url=item_icon,
            offer_state='Listed',
        )

        return True

    # print(item_id)
    # print(trade_url)
    # print(item_price)
    # print(item_name)
    # print(item_hash_name)
    # print(item_icon)



    