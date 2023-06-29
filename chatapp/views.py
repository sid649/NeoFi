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
from django.http import JsonResponse
import json
import os


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


class GetOnlineUsers(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):

        online_users = self.queryset.filter(status='online')
        if online_users:
            return online_users
        else:
            return Response({'message':'No online user found'}, status=status.HTTP_400_BAD_REQUEST)
        

class ChatStartView(APIView):
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
        

class ChatSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        recipient = request.data.get('receiver')
        message = request.data.get('message')

        recipient_obj = User.objects.filter(username=recipient).first()

        if not recipient_obj:
            return Response({'status': 'error', 'message': 'User does not exists'})

        # Check if recipient is online
        if recipient_obj.status == 'online':
            channel_layer = get_channel_layer()
            # Send message to recipient
            async_to_sync(channel_layer.group_send)(
                f'chat_{recipient}',
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
            return Response({'status': 'success', 'message': 'Message sent successfully'})

        return Response({'status': 'error', 'message': 'Recipient is offline'})
    

    
class SuggestedFriendsView(APIView):
    def get(self, request, user_id):
        
        file_path = os.path.join(os.path.dirname(__file__), 'suggested_friends.json')
        
        # Load user data from the JSON file
        with open(file_path) as json_file:
            user_data = json.load(json_file)

        # Iterate over (Used for performance aspect)
        user = next((user for user in user_data['users'] if user['id'] == user_id))
        
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Calculate similarity scores for each user and sort them in descending order
        suggested_friends = []
        for other_user in user_data['users']:
            if other_user['id'] != user_id:
                similarity_score = calculate_similarity(user, other_user)
                suggested_friends.append((other_user, similarity_score))
        
        suggested_friends = sorted(suggested_friends, key=lambda x: x[1], reverse=True)
        
        # Get the top 5 recommended friends
        top_5_friends = [friend[0] for friend in suggested_friends[:5]]
        
        return JsonResponse({'suggested_friends': top_5_friends})

def calculate_similarity(user1, user2):
    similarity_score = 0
    for interest in user1['interests']:
        if interest in user2['interests']:
            similarity_score += abs(user1['interests'][interest] - user2['interests'][interest])
    
    return similarity_score