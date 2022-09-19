from django.urls import path, include
from . import views

app_name = "withdraw"

urlpatterns = [
    path('', views.withdrawOptions, name="withdraw"),
    path('crypto/btc/', views.withdrawBtc, name="withdraw-crypto-btc"),
    path('skins/', views.withdrawCSGOskins, name="withdraw-skins"),
]