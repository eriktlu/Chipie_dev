from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('profile/', views.profile, name="profile"),

    path('logout/', views.logoutUser, name="logout"),
    path('', include('social_django.urls', namespace='social')),
    path('api/coins/', views.get_coins, name="get-coins"),


    # Nii saad lisada uut urli. Peab alati l6ppema '/'. path('url-mis-lisad/', views.funktsiooniNimi, name="nimi, millega lehel linkid sellel urlile")
    path('privacy-policy/', views.privacyPolicy, name="privacypolicy"),
    path('fairness/', views.fairness, name="fairness")

]