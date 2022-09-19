from bit import PrivateKey, PrivateKeyTestnet, wif_to_key, Key
from bit.network import get_fee, get_fee_cached
from bit.network import currency_to_satoshi_cached

from decimal import Decimal

from .models import Withdraw
# L51NVA56DVQKyj1smooM7fV1iCdw5qu8tUwkRNmJJtNMZNCyxvQ1
# L1uV1ZXrAVFQyrvG3ko7ezL6hgvAPBkCk1gej4mUzbZ6eBQjFR6v

from test_cs import settings

def BtcWithdraw(wallet_address, gold_amount, steam_id, country_code):
    # print(settings.PRIVATE_KEY_BTC)
    # key = Key('L1uV1ZXrAVFQyrvG3ko7ezL6hgvAPBkCk1gej4mUzbZ6eBQjFR6v')
    # key.get_balance('usd')
    # print(key)
    # print(key.address)
    # print(key.get_balance('btc'))
    # print(key.get_unspents())
    # print(key.get_transactions())

    test = int(gold_amount) / 10

    # test_key = PrivateKeyTestnet()
    # print(test_key)
    # print(test_key.address)
    # print(test_key.to_wif())
    # print(test_key.get_balance('btc'))

    my_key = PrivateKeyTestnet('cUHGdWiJ7KDMLwGPQEuPsw2YT5XdyaLw6x2p2a6XCG1YWbj6TW2E')
    # print(my_key)
    # print(my_key.to_wif())
    # print(my_key.version)
    # print(my_key.get_balance('btc'))
    # print(my_key.address)
    # print(my_key.balance_as('usd'))
    # print(currency_to_satoshi_cached(gold_amount, 'eur'))
    btc_to_send = currency_to_satoshi_cached(test, 'usd') / 100000000
    print(btc_to_send)

    # eur_value = gold_amount / 10

    test = my_key.send([(wallet_address, gold_amount, 'usd')])
    # print(get_fee(fast=False))
    # print(get_fee_cached())

    # print(key.get_transactions())
    # print(key.get_balance('mbtc'))
    # print(key.balance)
    # print(key.balance_as('usd'))

    # key.send([('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 5, 'usd')])



    Withdraw.objects.create(
        steam_id = steam_id,
        transaction_value_crypto = Decimal(btc_to_send),
        crypto_type = 'BTC',
        transaction_value_gold = Decimal(gold_amount),
        country_code = country_code
    )

    return test