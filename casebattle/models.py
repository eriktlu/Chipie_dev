from django.db import models

from main.models import CustomUser

class CaseBattleChests(models.Model):
    name = models.CharField(max_length=64)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class CaseBattlePackages(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    avatar = models.CharField(max_length=64, default='images/1.png')

    chest = models.ForeignKey(CaseBattleChests, on_delete=models.CASCADE, related_name="casebattle_packages_chest")

    def __str__(self):
        return self.name

# class CaseBattleClientSeed(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="casebattle_client_seed_user")
#     client_seed = models.CharField(max_length=32)

#     seed_generated_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.client_seed

class CaseBattleServerSeed(models.Model):
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="casebattle_server_seed_user")
    server_seed = models.CharField(max_length=64)
    hashed_server_seed = models.CharField(max_length=64)

    seed_generated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.server_seed

class CaseBattleRoom(models.Model):
    room_creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="casebattle_room_creator")
    package = models.ForeignKey(CaseBattlePackages, on_delete=models.CASCADE, related_name="casebattle_package_name")

    room_name = models.CharField(max_length=10)
    round_number = models.IntegerField(unique=True, default=0)

    battle_state = models.CharField(max_length=20)
    battle_result_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    winner_count = models.IntegerField(default=0)

    used_server_seed = models.ForeignKey(CaseBattleServerSeed, on_delete=models.CASCADE, related_name="casebattle_used_server_seed", blank=True, null=True)

    room_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_name

class CaseBattleChestItems(models.Model):
    chest = models.ForeignKey(CaseBattleChests, on_delete=models.CASCADE, related_name="casebattle_chest")

    item_name = models.CharField(max_length=64)
    item_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.CharField(max_length=512, default="test.com")
    exterior_name = models.CharField(max_length=128, default="test.com")
    skinline_name = models.CharField(max_length=128, default="Crimson Web")
    skinline_color = models.CharField(max_length=10, default="#4051F0")
    


    item_odds = models.DecimalField(max_digits=15, decimal_places=10)

    def __str__(self):
        return self.item_name

class CaseBattle(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="casebattle_user")
    room = models.ForeignKey(CaseBattleRoom, on_delete=models.CASCADE, related_name="casebattle_room")
    room_seat = models.IntegerField(default=0)

    roll_1 = models.ForeignKey(CaseBattleChestItems, on_delete=models.CASCADE, related_name="casebattle_rolled_item_1", null=True, blank=True)
    roll_2 = models.ForeignKey(CaseBattleChestItems, on_delete=models.CASCADE, related_name="casebattle_rolled_item_2", null=True, blank=True)
    roll_3 = models.ForeignKey(CaseBattleChestItems, on_delete=models.CASCADE, related_name="casebattle_rolled_item_3", null=True, blank=True)
    roll_4 = models.ForeignKey(CaseBattleChestItems, on_delete=models.CASCADE, related_name="casebattle_rolled_item_4", null=True, blank=True)
    roll_5 = models.ForeignKey(CaseBattleChestItems, on_delete=models.CASCADE, related_name="casebattle_rolled_item_5", null=True, blank=True)

    battle_result = models.CharField(max_length=20, blank=True)
    battle_result_coins = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    used_client_seed = models.CharField(max_length=64, blank=True)

    total_result = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    game = models.CharField(max_length=128, default='casebattle')

    created = models.DateTimeField(auto_now_add=True)

