from django.urls import path, include
from . import views

app_name = "deposit"

urlpatterns = [
    path('', views.depositOptions, name="deposit"),
    path('skins/', views.depositSkins, name="deposit-skins"),

    path('paypal/', views.depositPayPal, name="deposit-paypal"),
    path('paypal/complete/', views.paymentComplete, name="payment-complete"),

    path('successful/', views.paymentSuccessful, name="payment-successful"),
    path('cancelled/', views.paymentCancel, name="payment-cancel"),

    path('crypto/', views.cryptoPayment, name="deposit-crypto"),
    path('crypto/webhook/', views.coinbase_webhook, name='deposit-webhook'),
]