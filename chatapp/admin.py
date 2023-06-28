from django.contrib import admin
from .models import CustomUser, ChatMessage

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ChatMessage)