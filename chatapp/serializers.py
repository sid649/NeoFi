from rest_framework import serializers, validators
from .models import *

from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'status']

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
                'password': {
                    'write_only': True
                    },
                'username': {
                    'required': True,
                    'allow_blank': False,
                    'validators': [
                        validators.UniqueValidator(
                            User.objects.all(), 'User already exists'
                        )
                    ]
                }
            }

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = ['receiver', 'message']

        extra_kwargs = {'receiver': {'required': True,'allow_blank': False}}
        extra_kwargs = {'message': {'required': True,'allow_blank': False}}

    def create(self, validated_data):
        chat_message = ChatMessage.objects.create(sender=validated_data['sender'], receiver=validated_data['receiver'], message=validated_data['message'])
        chat_message.save()
        return chat_message