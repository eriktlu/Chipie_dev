from bitcash import Key, PrivateKey, PrivateKeyTestnet

from decimal import Decimal

from .models import Withdraw
# L51NVA56DVQKyj1smooM7fV1iCdw5qu8tUwkRNmJJtNMZNCyxvQ1
# L1uV1ZXrAVFQyrvG3ko7ezL6hgvAPBkCk1gej4mUzbZ6eBQjFR6v

from test_cs import settings

def BtchWithdraw(wallet_address, gold_amount, steam_id, country_code):

    print('bitcash')
    my_key = PrivateKeyTestnet()
    print(my_key.to_wif())
    print(my_key.address)
    print(my_key.balance_as('usd'))

    return