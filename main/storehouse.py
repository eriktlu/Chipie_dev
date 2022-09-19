import time, asyncio
from steampy.client import SteamClient, TradeOfferState, Asset
from steampy.utils import GameOptions
from .models import CustomUser, TradeOffers, CsgoItems
from .jobs import client

# Set API key
api_key = '38267258EDD06FDF65931B45C438228E'
# Set path to SteamGuard file
steamguard_path = './Steamguard.txt'
# Steam username
username = 'p6mm'
# Steam password
password = 'kitskaalikas1'

botLoggedIn = False
# client = SteamClient(api_key)
game = GameOptions.CS


def sendTradeDepositeSessionControl(user_id, item_name, trade_url):
    global botLoggedIn, client
    if botLoggedIn is False:
        client.login(username, password, steamguard_path)
        botLoggedIn = True
    
    if client.is_session_alive() == True:
        print('alive')
        sendTradeDeposite(user_id, item_name, trade_url)
    else:
        client.login(username, password, steamguard_path)
        print('reborn')
        sendTradeDeposite(user_id, item_name, trade_url)

def sendTradeDeposite(user_id, item_name, trade_url):
    # partner_id = '76561198051843941'
    game = GameOptions.CS

    my_items = ''

    user_items_frontend = item_name.copy()

    items_len = len(item_name)
    user_items = client.get_partner_inventory(user_id, game)
    user_items_list = iter(user_items.values())
    user_items_to_trade = []

    if len(item_name) <= 0:
        print("No items chosen")
        return

    for item in user_items_list:
        if item['tradable'] == 1:
            if item['market_hash_name'] in item_name:
                user_items_to_trade.append(Asset(item['id'], game))
                #print(item['market_hash_name'])
                item_name.remove(item['market_hash_name'])

    if items_len != len(user_items_to_trade):
        print("Couldn't find all the items from the partner inventory!")
        return

    itemsValueList = []
    for item in user_items_frontend:
        item_from_db = CsgoItems.objects.filter(market_hash_name=item)[0]
        itemsValueList.append(item_from_db.item_value)
    itemsValue = sum(itemsValueList)
    #userObj = CustomUser.objects.filter(steam_id=user_id)[0]
    
    client.make_offer_with_url(my_items, user_items_to_trade, trade_url, 'Deposite Offer')
    
    offers = client.get_trade_offers()
    #tradeOffers = TradeOffers.objects.filter(name__steam_id=user_id)[0]
    #print(tradeOffers.name.steam_id)

    for offer in offers['response']['trade_offers_sent']:
        convertSteamid = offer['accountid_other']
        convertSteamid += 76561197960265728

        print(convertSteamid)

        if int(user_id) == convertSteamid:
            if offer['trade_offer_state'] == 2:
                print("Found trade offer")
                user_obj = get_object(user_id)
                
                obj, created = TradeOffers.objects.get_or_create(offer_id=offer['tradeofferid'], defaults = {'name':user_obj, 'offer_state':offer['trade_offer_state'], 'offer_message':offer['message'], 'offer_value':itemsValue})
                
                if created:
                    print('Deposit offer was sent!')
                    # newBalance = userObj.user_coins + itemsValue
                    # CustomUser.objects.filter(steam_id=user_id).update(user_coins=newBalance)
                else:
                    print('Deposit offer was NOT sent!')
        else:
            print("Not for this user")


def sendTradeWithdrawSessionControl(user_id, item_name, trade_url):
    global botLoggedIn, client
    if botLoggedIn is False:
        client.login(username, password, steamguard_path)
        print('logged in first time')
        botLoggedIn = True
    
    if client.is_session_alive() == True:
        print('alive')
        sendTradeWithdraw(user_id, item_name, trade_url)
    else:
        client.login(username, password, steamguard_path)
        print('reborn')
        sendTradeWithdraw(user_id, item_name, trade_url)

def sendTradeWithdraw(user_id, item_name, trade_url):
    # partner_tradeoffer_url = 'https://steamcommunity.com/tradeoffer/new?partner=91578213&token=Rp_tzpM_'
    game = GameOptions.CS

    user_selected_items_frontend = item_name.copy()

    items_len = len(item_name)
    bot_items = client.get_my_inventory(game)
    bot_items_list = iter(bot_items.values())
    bot_items_to_trade = []

    for item in bot_items_list:
        if item['tradable'] == 1:
            if item['market_hash_name'] in item_name:
                bot_items_to_trade.append(Asset(item['id'], game))
                #print(item['market_hash_name'])
                item_name.remove(item['market_hash_name'])
    
    if items_len <= 0:
        print("No items chosen")
        return

    if items_len != len(bot_items_to_trade):
        print("Couldn't find all the items from the Bot inventory!")
        return

    itemsValueList = []
    for item in user_selected_items_frontend:
        item_from_db = CsgoItems.objects.filter(market_hash_name=item)[0]
        itemsValueList.append(item_from_db.item_value)
    itemsValue = sum(itemsValueList)

    userObj = CustomUser.objects.filter(steam_id=user_id)[0]
    if userObj.user_coins < itemsValue:
        print("User didn't have enough coins!")
    else:
        client.make_offer_with_url(bot_items_to_trade, '', trade_url, 'Withdraw Offer')

        offers = client.get_trade_offers()
        #tradeOffers = TradeOffers.objects.filter(name__steam_id=user_id)[0]
        #print(tradeOffers.name.steam_id)

        # test_id = 76561198051843941

        for offer in offers['response']['trade_offers_sent']:
            convertSteamid = offer['accountid_other']
            convertSteamid += 76561197960265728

            if int(user_id) == convertSteamid:
                if offer['trade_offer_state'] == 2:
                    print("Found trade offer")
                    user_obj = get_object(user_id)
                    obj, created = TradeOffers.objects.get_or_create(offer_id=offer['tradeofferid'], defaults = {'name':user_obj, 'offer_state':offer['trade_offer_state'], 'offer_message':offer['message'], 'offer_value':itemsValue})
                    
                    if created:
                        print('Withdraw offer was sent!')
                        newBalance = userObj.user_coins - itemsValue
                        CustomUser.objects.filter(steam_id=user_id).update(user_coins=newBalance)
                    else:
                        print('Withdraw offer was NOT sent!')
            else:
                print("Not for this user")
        
    

def get_object(name):
        return CustomUser.objects.get(name=name)


# asyncio.run(sendTradeOffersSessionControl())