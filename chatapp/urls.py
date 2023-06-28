from django.urls import path, include
from .views import *
from knox import views as knox_views
from . import routing

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register_view'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout_view'),
    path('get-online-users/', getOnlineUsers.as_view({'get': 'list'}), name='get_online_users'),
    path('chat/start/', chatStartView.as_view(), name='chat_start_view'),
    path('chat/send/', SendChatView.as_view(), name='send_chat_view'),
]
