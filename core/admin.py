from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Profile, Post, LikePost, Group,Thread, ChatMessage, Partido, Reporte

# Registrar el modelo Group
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'creator', 'created_at')
    search_fields = ('group_name', 'creator__username')
    list_filter = ('created_at',)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(Group, GroupAdmin)
admin.site.register(ChatMessage)
admin.site.register(Partido)
admin.site.register(Reporte)

class ChatMessage(admin.TabularInline):
    model = ChatMessage

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)

