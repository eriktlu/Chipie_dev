from .models import CustomUser


def save_profile(backend, username, details, response, *args, **kwargs):
    print(details['player'])
    CustomUser.objects.get_or_create(
        name = details['player']['steamid'],
        username = username,
        steam_id = details['player']['steamid'],
        player = details['player'],
    )

    
