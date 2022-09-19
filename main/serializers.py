from rest_framework.serializers import ModelSerializer
from .models import CustomUser, Messages

class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class MessagesSerializer(ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'