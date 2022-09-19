from django.contrib.auth.base_user import BaseUserManager

from django.utils.crypto import get_random_string

# from casebattle.models import CaseBattleClientSeed
# from .models import CustomUser

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password, is_staff, is_superuser, **extra_fields):
        if not username:
            raise ValueError('Steam name must be set')
        user = self.model(
            username=username,
            name=extra_fields['player']['steamid'],
            steam_id=extra_fields['player']['steamid'],
            avatar=extra_fields['player']['avatarmedium'],
            user_coins=2000.00,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            player=extra_fields['player'],
            )
        if password:
            user.set_password(password)
        else:
            user.set_password(None)
        user.save(using=self._db)

        # userObj = CustomUser.objects.filter(steam_id=extra_fields['player']['steamid'])[0]

        # client_seed = get_random_string(length=32)
        # cb_client_seed = CaseBattleClientSeed(user=userObj, client_seed=client_seed)
        # cb_client_seed.save()

        return user

    def create_user(self, password=None, **extra_fields):
        return self._create_user(extra_fields['name'], password, False, False, **extra_fields)

    def create_superuser(self, name, password, **extra_fields):
        # if not username:
        #     raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have a password")
        if not name:
            raise ValueError("User must have a name")
        
        print(password)

        user = self.model(
            name = name
        )
        
        user.username = 'username'
        user.set_password(password)
        user.is_staff = True
        user.active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user