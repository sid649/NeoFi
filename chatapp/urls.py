from django.urls import path, include
from .views import *
from knox import views as knox_views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register_view'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout_view'),
    path('get-online-users/', GetOnlineUsers.as_view({'get': 'list'}), name='get_online_users'),
    path('chat/start/', ChatStartView.as_view(), name='chat_start_view'),
    path('chat/send/', ChatSendView.as_view(), name='send_chat_view'),
    path('suggested-friends/<int:user_id>/', SuggestedFriendsView.as_view(), name='suggested_friends_view')
]
