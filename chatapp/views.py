from .serializers import RegisterSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from .models import ChatMessage


User = get_user_model()


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        _, token = AuthToken.objects.create(user)

        return Response({
            'user_info':{
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
            'token': token,
            'message': 'User created successfully'
        },
        status=status.HTTP_200_OK
        )



class LoginView(APIView):
    
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        _, token = AuthToken.objects.create(user)

        return Response({
            'user_info':{
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token,
            'message': 'Login Successful'
        },
        status=status.HTTP_200_OK
        )


class getOnlineUsers(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):

        online_users = self.queryset.filter(status='online')
        if online_users:
            return online_users
        else:
            return Response({'message':'No online user found'}, status=status.HTTP_400_BAD_REQUEST)
        

class chatStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        sender = request.user.username
        receiver = request.data.get('receiver')

        # Check the status of the receiver
        try:
            receiver_user = User.objects.get(username=receiver)
            if receiver_user.status == 'online':
                
                return Response({'status': 'success', 'message': message, 'sender': sender, 'receiver': receiver_user.username})
            else:
                return Response({'status': 'error', 'message': 'Receiver is offline'})
            
        except User.DoesNotExist:
            
            return Response({'status': 'error', 'message': 'Receiver not found'})
        

class SendChatView(APIView):
    authentication_classes = [permissions.IsAuthenticated]

    def post(request, chat_id):
        chat = get_object_or_404(ChatMessage, id=chat_id)
        channel_layer = get_channel_layer()

        async def send_message():
            await channel_layer.group_send(
                f'chat_{chat_id}',
                {
                    'type': 'chat_message',
                    'message': request.POST['message'],
                    'sender': request.user.username,
                }
            )

        database_sync_to_async(send_message)()
        return HttpResponse(status=200)